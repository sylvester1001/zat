/**
 * 副本配置
 * 新增副本时只需在此文件添加配置即可
 */

export type DifficultyId = 'normal' | 'hard' | 'nightmare';

export interface Difficulty {
  id: DifficultyId;
  name: string;
  color: string; // CSS 类名
}

export interface Dungeon {
  id: string;
  name: string;
  desc: string;
  bgClass: string;
  difficulties: DifficultyId[];
}

// 难度定义
export const DIFFICULTIES: Record<DifficultyId, Difficulty> = {
  normal: { id: 'normal', name: '普通', color: 'difficulty-normal' },
  hard: { id: 'hard', name: '困难', color: 'difficulty-hard' },
  nightmare: { id: 'nightmare', name: '噩梦', color: 'difficulty-nightmare' },
};

// 副本配置 (ID 需要和后端 scene_graph.py 一致)
export const DUNGEONS: Dungeon[] = [
  {
    id: 'world_tree',
    name: '世界之树',
    desc: '魔物隐藏于树荫之下，唯有深入才能将其消灭',
    bgClass: 'world_tree-bg',
    difficulties: ['normal', 'hard'],
  },
  {
    id: 'mount_mechagod',
    name: '机神山',
    desc: '向古老试炼之地发起挑战，只有胜者能获得一切',
    bgClass: 'mount_mechagod-bg',
    difficulties: ['normal', 'hard'],
  },
  {
    id: 'sea_palace',
    name: '海之宫遗迹',
    desc: '原本只存在于传说中的古之宫殿，埋藏着无数珍宝',
    bgClass: 'sea_palace-bg',
    difficulties: ['normal', 'hard'],
  },
  {
    id: 'mizumoto_shrine',
    name: '源水大社',
    desc: '供奉河川神明之所，最深处被强悍的古代构造体守护着',
    bgClass: 'mizumoto_shrine-bg',
    difficulties: ['normal', 'hard', 'nightmare'],
  },
];

// 获取副本的难度列表
export function getDungeonDifficulties(dungeonId: string): Difficulty[] {
  const dungeon = DUNGEONS.find(d => d.id === dungeonId);
  if (!dungeon) return [];
  return dungeon.difficulties.map(id => DIFFICULTIES[id]);
}
