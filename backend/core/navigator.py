# 场景导航器
# 负责场景识别、寻路和导航

import asyncio
import logging
from collections import deque
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.adb_controller import ADBController
    from core.image_matcher import ImageMatcher

from core.scene_registry import registry, Scene, Transition, ActionType
from core.scene_observer import SceneObserver

# 导入场景定义（触发注册）
import scenes

logger = logging.getLogger("zat.navigator")


class Navigator:
    # 场景导航器：基于观察的贪婪导航策略
    
    def __init__(self, adb: "ADBController", matcher: "ImageMatcher"):
        self.adb = adb
        self.matcher = matcher
        self.observer = SceneObserver(adb, matcher)
    
    def find_path(self, from_scene: str, to_scene: str) -> Optional[list[str]]:
        # 使用 BFS 寻找最短路径
        # Returns: 场景ID列表（包含起点和终点），无法到达返回 None
        
        if from_scene == to_scene:
            return [from_scene]
        
        if not registry.get(from_scene) or not registry.get(to_scene):
            return None
        
        queue = deque([(from_scene, [from_scene])])
        visited = {from_scene}
        
        while queue:
            current, path = queue.popleft()
            scene = registry.get(current)
            
            if not scene:
                continue
            
            # 检查所有可转移的场景
            for target_id in scene.transitions.keys():
                if target_id == to_scene:
                    return path + [target_id]
                
                if target_id not in visited and registry.get(target_id):
                    visited.add(target_id)
                    queue.append((target_id, path + [target_id]))
            
            # 也考虑返回操作
            if scene.back_to and scene.back_to not in visited:
                if scene.back_to == to_scene:
                    return path + [scene.back_to]
                visited.add(scene.back_to)
                queue.append((scene.back_to, path + [scene.back_to]))
        
        return None
    
    async def navigate_to(self, target: str, max_retry: int = 20) -> bool:
        # 导航到目标场景（贪婪策略：每步重新观察）
        # Returns: 成功返回 True
        
        stuck_count = 0
        last_scene = None
        
        while max_retry > 0:
            # 1. 每次都重新观察当前位置
            current = await self.observer.observe()
            
            # 2. 到达目标？
            if current == target:
                scene = registry.get(target)
                logger.info(f"成功到达: {scene.name if scene else target}")
                return True
            
            # 3. 检测是否卡住
            if current == last_scene and current != "unknown":
                stuck_count += 1
                if stuck_count >= 3:
                    logger.warning(f"卡在 {current}，尝试返回")
                    await self._press_back()
                    stuck_count = 0
                    max_retry -= 1
                    continue
            else:
                stuck_count = 0
            last_scene = current
            
            # 4. 无法识别？尝试处理
            if current == "unknown":
                await self._handle_unknown()
                max_retry -= 1
                continue
            
            # 5. 计算路径
            path = self.find_path(current, target)
            if not path or len(path) < 2:
                logger.warning(f"无法从 {current} 到达 {target}")
                await self._handle_unknown()
                max_retry -= 1
                continue
            
            # 6. 只执行第一步
            next_scene = path[1]
            current_scene_obj = registry.get(current)
            
            if not current_scene_obj:
                max_retry -= 1
                continue
            
            # 获取转移定义
            transition = current_scene_obj.transitions.get(next_scene)
            if not transition and current_scene_obj.back_to == next_scene:
                # 使用返回操作
                transition = Transition(
                    target=next_scene,
                    action=ActionType.BACK,
                    template=current_scene_obj.back_template,
                )
            
            if transition:
                logger.info(f"执行: {current_scene_obj.name} -> {registry.get(next_scene).name}")
                await self._execute_transition(transition)
            
            max_retry -= 1
        
        logger.error(f"导航失败: 无法到达 {target}")
        return False
    
    async def detect_current_scene(self) -> str:
        # 检测当前场景
        return await self.observer.observe()
    
    async def click_template(self, template_name: str, timeout: float = 5.0, threshold: float = 0.7) -> bool:
        # 等待并点击模板（对外 API）
        return await self._click_template(template_name, timeout, threshold)
    
    async def click_template_if_exists(self, screen, template_name: str, threshold: float = 0.7) -> bool:
        # 检测模板存在则点击（单次检测，不等待）
        result = self.matcher.match_template(screen, template_name, threshold=threshold)
        if result:
            x, y, _ = result
            await self.adb.tap(x, y)
            logger.debug(f"点击: {template_name} at ({x}, {y})")
            return True
        return False
    
    async def press_back(self) -> bool:
        # 按返回键（对外 API）
        return await self._press_back()
    
    def get_scene_info(self, scene_id: str) -> Optional[dict]:
        # 获取场景信息
        scene = registry.get(scene_id)
        if scene:
            return {
                "id": scene.id,
                "name": scene.name,
                "fingerprint": scene.fingerprint,
                "transitions": list(scene.transitions.keys()),
                "back_to": scene.back_to,
            }
        return None
    
    def get_all_scenes(self) -> list[str]:
        # 获取所有已注册的场景ID
        return list(registry.get_all().keys())
    
    def get_current_scene(self) -> Optional[str]:
        # 获取当前场景（新架构不缓存状态，返回 None 让调用方使用 detect_current_scene）
        return None
    
    # ==================== 内部方法 ====================
    
    async def _execute_transition(self, transition: Transition) -> bool:
        # 执行场景转移操作
        try:
            # 先滑动（如果需要）
            if transition.scroll:
                await self._scroll(transition.scroll, transition.scroll_distance)
                await asyncio.sleep(0.3)
            
            success = False
            
            if transition.action == ActionType.CLICK:
                if transition.template:
                    success = await self._click_template(transition.template)
                    
            elif transition.action == ActionType.CLICK_TEXT:
                if transition.text:
                    success = await self._click_text(transition.text)
                    
            elif transition.action == ActionType.BACK:
                if transition.template:
                    success = await self._click_template(transition.template)
                else:
                    success = await self._press_back()
                    
            elif transition.action == ActionType.SWIPE:
                await self._scroll(transition.scroll or "down", transition.scroll_distance)
                success = True
            
            if success:
                await asyncio.sleep(transition.wait_after)
            
            return success
            
        except Exception as e:
            logger.error(f"执行转移失败: {e}")
            return False
    
    async def _click_template(self, template_name: str, timeout: float = 5.0, threshold: float = 0.7) -> bool:
        # 等待并点击模板
        elapsed = 0
        interval = 0.3
        
        while elapsed < timeout:
            screen = await self.adb.screencap_array()
            result = self.matcher.match_template(screen, template_name, threshold=threshold)
            
            if result:
                x, y, _ = result
                await self.adb.tap(x, y)
                logger.debug(f"点击: {template_name} at ({x}, {y})")
                return True
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        logger.warning(f"未找到模板: {template_name}")
        return False
    
    async def _click_text(self, text: str, timeout: float = 5.0) -> bool:
        # 点击文字
        elapsed = 0
        interval = 0.5
        
        while elapsed < timeout:
            screen = await self.adb.screencap_array()
            result = self.matcher.ocr_find_text(screen, text)
            
            if result:
                x, y, _ = result
                await self.adb.tap(x, y)
                logger.debug(f"点击文字: {text} at ({x}, {y})")
                return True
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        logger.warning(f"未找到文字: {text}")
        return False
    
    async def _scroll(self, direction: str, distance: int = 500):
        # 滑动屏幕
        screen = await self.adb.screencap_array()
        h, w = screen.shape[:2]
        
        start_x = w // 2
        start_y = h // 2
        
        if direction == "down":
            end_y = start_y + distance
        elif direction == "up":
            end_y = start_y - distance
        else:
            return
        
        await self.adb.swipe(start_x, start_y, start_x, end_y, duration=300)
        await asyncio.sleep(0.5)
    
    async def _press_back(self) -> bool:
        # 按返回键
        cmd = f'"{self.adb.adb_path}" -s {self.adb.device} shell input keyevent KEYCODE_BACK'
        await self.adb._run_command(cmd)
        logger.debug("按下返回键")
        return True
    
    async def _handle_unknown(self):
        # 处理未知状态：尝试关闭弹窗或返回
        logger.info("尝试处理未知状态...")
        
        screen = await self.adb.screencap_array()
        
        # 尝试点击关闭按钮
        for close_template in ["close", "back"]:
            result = self.matcher.match_template(screen, close_template, threshold=0.7)
            if result:
                x, y, _ = result
                await self.adb.tap(x, y)
                logger.debug(f"点击关闭: {close_template}")
                await asyncio.sleep(0.5)
                return
        
        # 尝试按返回键
        await self._press_back()
        await asyncio.sleep(0.5)
