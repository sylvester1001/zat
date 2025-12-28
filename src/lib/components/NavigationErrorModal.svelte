<script lang="ts">
  import { Modal, Button } from 'flowbite-svelte';
  import { ExclamationCircleOutline } from 'flowbite-svelte-icons';
  
  export let open = false;
  export let message = '';
  export let onRetry: () => void = () => {};
  export let onCancel: () => void = () => {};
  
  function handleRetry() {
    open = false;
    onRetry();
  }
  
  function handleCancel() {
    open = false;
    onCancel();
  }
</script>

<Modal bind:open size="sm" autoclose={false} class="w-full">
  <div class="text-center">
    <ExclamationCircleOutline class="mx-auto mb-4 text-orange-400 w-12 h-12" />
    <h3 class="mb-5 text-lg font-normal text-gray-400">
      导航失败
    </h3>
    <p class="mb-5 text-sm text-gray-500">
      {message || `无法导航到目标场景，已回退到主界面`}
    </p>
    <div class="flex justify-center gap-4">
      <Button color="primary" onclick={handleRetry}>重试</Button>
      <Button color="alternative" onclick={handleCancel}>取消</Button>
    </div>
  </div>
</Modal>
