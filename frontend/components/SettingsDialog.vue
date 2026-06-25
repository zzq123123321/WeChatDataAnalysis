<template>
  <div
    v-if="open"
    class="settings-dialog fixed inset-0 z-[120] flex items-center justify-center bg-black/40 px-4 py-4 backdrop-blur-md sm:py-8"
    @click.self="handleClose"
  >
    <div class="settings-dialog-panel flex h-[80vh] min-h-[380px] w-full max-w-[880px] overflow-hidden rounded-[10px] border border-[#e2e2e2] bg-white shadow-2xl">
      <!-- Sidebar -->
      <aside class="flex w-[160px] shrink-0 flex-col bg-[#fcfcfc] border-r border-[#eeeeee]">
        <div class="mt-4 mb-2 flex items-center px-4 gap-2">
          <div class="flex h-6 w-6 items-center justify-center rounded-[5px] bg-[#e7f5ee] text-[#07b75b]">
            <svg class="h-[15px] w-[15px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span class="text-[14px] font-bold text-[#1f1f1f]">设置</span>
        </div>

        <div class="flex-1 space-y-0.5 px-3 py-2 overflow-y-auto scrollbar-custom">
          <button
            v-for="item in settingNavItems"
            :key="item.key"
            type="button"
            class="group flex w-full flex-col items-start rounded-[6px] px-3 py-1.5 text-left transition select-none"
            :class="activeSection === item.key ? 'bg-white shadow-sm ring-1 ring-[#e5e5e5]' : 'hover:bg-[#f0f0f0]/60'"
            @click="scrollToSection(item.key)"
          >
            <div class="text-[12px] font-medium" :class="activeSection === item.key ? 'text-[#111]' : 'text-[#777] group-hover:text-[#333]'">
              {{ item.label }}
            </div>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="relative flex min-w-0 flex-1 flex-col bg-white">
        <button
          type="button"
          class="absolute right-3 top-3 z-10 flex h-6 w-6 items-center justify-center rounded-md text-[#888] transition hover:bg-[#f2f2f2] hover:text-[#222]"
          title="关闭设置"
          @click="handleClose"
        >
          <svg class="h-[14px] w-[14px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>

        <header class="flex h-12 shrink-0 items-center px-6">
          <div class="flex items-center gap-1.5 text-[#111]">
            <svg class="h-[15px] w-[15px] text-[#666]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h2 class="text-[13px] font-bold">{{ settingNavItems.find(i => i.key === activeSection)?.label || '设置' }}</h2>
          </div>
        </header>

        <div ref="contentScrollRef" class="scrollbar-custom flex-1 overflow-y-auto px-6 pb-8 pt-1 space-y-8" @scroll="onContentScroll">
          
          <div v-if="!isDesktopEnv" class="rounded-[6px] border border-amber-200 bg-amber-50 px-3 py-1.5 text-[11px] leading-relaxed text-amber-900">
            当前为浏览器环境：开机自启动/关闭窗口/更新 不可用；“启动偏好”可正常使用；“后端端口”会尝试同步重启本机后端到新端口。
          </div>

          <section ref="desktopSectionRef">
            <div class="mb-2.5 text-[12px] font-bold text-[#999] tracking-widest">桌面行为</div>
            <div class="overflow-hidden rounded-[10px] border border-[#e7e7e7] bg-white divide-y divide-[#ececec]">
              <div class="px-3.5 py-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">开机自启动</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">系统登录后自动启动桌面端应用</div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="desktopAutoLaunch"
                    class="settings-switch shrink-0"
                    :class="switchTrackClass(desktopAutoLaunch, !isDesktopEnv || desktopAutoLaunchLoading)"
                    :disabled="!isDesktopEnv || desktopAutoLaunchLoading"
                    @click="toggleDesktopAutoLaunch"
                  >
                    <span class="settings-switch-thumb" :class="desktopAutoLaunch ? 'translate-x-[20px]' : 'translate-x-0'" />
                  </button>
                </div>
                <div v-if="desktopAutoLaunchError" class="mt-1.5 text-[11px] text-red-600 whitespace-pre-wrap">
                  {{ desktopAutoLaunchError }}
                </div>
              </div>

              <div class="px-3.5 py-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">关闭窗口行为</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">点击关闭按钮时：默认最小化到托盘</div>
                  </div>
                  <select
                    class="shrink-0 rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30"
                    :disabled="!isDesktopEnv || desktopCloseBehaviorLoading"
                    :value="desktopCloseBehavior"
                    @change="onDesktopCloseBehaviorChange"
                  >
                    <option value="tray">最小化到托盘</option>
                    <option value="exit">直接退出</option>
                  </select>
                </div>
                <div v-if="desktopCloseBehaviorError" class="mt-1.5 text-[11px] text-red-600 whitespace-pre-wrap">
                  {{ desktopCloseBehaviorError }}
                </div>
              </div>

              <div class="px-3.5 py-3">
                <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:justify-between">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">后端端口</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">桌面端：重启内置后端并刷新；网页端：尝试切换端口</div>
                  </div>
                  <div class="flex shrink-0 items-center gap-1.5">
                    <input
                      v-model="desktopBackendPortInput"
                      type="number"
                      min="1"
                      max="65535"
                      class="w-16 rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-center text-[12px] tabular-nums text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30"
                      :disabled="desktopBackendPortLoading || desktopBackendPortApplying"
                      @keyup.enter="onDesktopBackendPortApply"
                    />
                    <button
                      type="button"
                      class="rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                      :disabled="desktopBackendPortLoading || desktopBackendPortApplying"
                      @click="onDesktopBackendPortApply"
                    >
                      {{ desktopBackendPortApplying ? '...' : '应用' }}
                    </button>
                    <button
                      type="button"
                      class="rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                      :disabled="desktopBackendPortLoading || desktopBackendPortApplying"
                      @click="onDesktopBackendPortReset"
                    >
                      恢复默认
                    </button>
                  </div>
                </div>
                <div v-if="desktopBackendPortError" class="mt-1.5 text-[11px] text-red-600 whitespace-pre-wrap">
                  {{ desktopBackendPortError }}
                </div>
              </div>

              <div class="px-3.5 py-3">
                <div class="flex flex-col gap-2.5">
                  <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:justify-between">
                    <div class="min-w-0 flex-1">
                      <div class="text-[13px] font-medium text-[#222]">output 目录</div>
                      <div class="mt-0.5 text-[11px] text-[#909090] break-words">
                        当前：{{ desktopOutputDirText }}
                        <span class="ml-1 text-[#666]">{{ desktopOutputDirIsDefault ? '（默认位置）' : '（自定义位置）' }}</span>
                      </div>
                      <div class="mt-0.5 text-[11px] text-[#909090] break-words">默认：{{ desktopOutputDirDefaultText }}</div>
                      <div v-if="desktopOutputDirPendingText" class="mt-0.5 text-[11px] text-amber-700 break-words">
                        待应用：{{ desktopOutputDirPendingText }}
                      </div>
                      <div v-if="desktopOutputDirUnavailableReason" class="mt-1 text-[11px] text-amber-700 break-words">
                        {{ desktopOutputDirUnavailableReason }}
                      </div>
                    </div>
                    <button
                      type="button"
                      class="shrink-0 rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                      :disabled="!isDesktopEnv || desktopOutputDirLoading || desktopOutputDirApplying"
                      @click="onDesktopOpenOutputDir"
                    >
                      打开当前 output
                    </button>
                  </div>
                  <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center">
                    <input
                      v-model="desktopOutputDirInput"
                      type="text"
                      spellcheck="false"
                      class="min-w-0 flex-1 rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30"
                      :disabled="desktopOutputDirControlsDisabled"
                      :placeholder="desktopOutputDirCanChange ? '选择新的 output 目录' : '当前环境不支持修改 output 目录'"
                      @keyup.enter="onDesktopOutputDirApply"
                    />
                    <div class="flex shrink-0 items-center gap-1.5">
                      <button
                        type="button"
                        class="rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="desktopOutputDirControlsDisabled"
                        @click="onDesktopChooseOutputDir"
                      >
                        选择文件夹
                      </button>
                      <button
                        type="button"
                        class="rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="desktopOutputDirControlsDisabled"
                        @click="onDesktopOutputDirApply"
                      >
                        {{ desktopOutputDirApplying ? '迁移中...' : '应用' }}
                      </button>
                      <button
                        type="button"
                        class="rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="desktopOutputDirControlsDisabled"
                        @click="onDesktopOutputDirReset"
                      >
                        恢复默认
                      </button>
                    </div>
                  </div>
                  <div v-if="desktopOutputDirCanChange" class="text-[11px] text-[#909090]">
                    修改后会迁移整个 output 目录；如果目标目录已有内容，会先阻止并提示。
                  </div>
                  <div v-if="desktopOutputDirProgress" class="rounded-[6px] border border-[#d8efe2] bg-[#f4fbf7] px-2.5 py-2">
                    <div class="flex items-center justify-between gap-3 text-[11px] text-[#1b6b43]">
                      <div class="min-w-0 truncate">{{ desktopOutputDirProgressText }}</div>
                      <div class="shrink-0 tabular-nums">{{ desktopOutputDirProgressPercentText }}</div>
                    </div>
                    <div class="mt-1.5 h-2 overflow-hidden rounded-full bg-[#dceee3]">
                      <div
                        class="h-full rounded-full bg-[#07b75b] transition-[width] duration-200 ease-out"
                        :class="desktopOutputDirProgressIndeterminate ? 'animate-pulse' : ''"
                        :style="{ width: desktopOutputDirProgressBarWidth }"
                      />
                    </div>
                    <div v-if="desktopOutputDirProgressDetail" class="mt-1 text-[10px] text-[#5d7a68] break-all">
                      {{ desktopOutputDirProgressDetail }}
                    </div>
                  </div>
                  <div v-if="desktopOutputDirMessage" class="rounded-[6px] border border-[#d8efe2] bg-[#f4fbf7] px-2.5 py-1.5 text-[11px] text-[#1b6b43] whitespace-pre-wrap">
                    {{ desktopOutputDirMessage }}
                  </div>
                </div>
                <div v-if="desktopOutputDirError" class="mt-1.5 text-[11px] text-red-600 whitespace-pre-wrap">
                  {{ desktopOutputDirError }}
                </div>
              </div>

              <div class="px-3.5 py-3">
                <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:justify-between">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">日志文件</div>
                    <div class="mt-0.5 text-[11px] text-[#909090] break-words">{{ desktopLogFileText }}</div>
                  </div>
                  <button
                    type="button"
                    class="shrink-0 rounded-[6px] border border-[#e2e2e2] bg-white px-2 py-1 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="desktopLogFileLoading || desktopLogFileOpening"
                    @click="onOpenBackendLogFile"
                  >
                    {{ desktopLogFileOpening ? '打开中...' : '打开日志' }}
                  </button>
                </div>
                <div v-if="desktopLogFileError" class="mt-1.5 text-[11px] text-red-600 whitespace-pre-wrap">
                  {{ desktopLogFileError }}
                </div>
              </div>
            </div>
          </section>

          <section ref="startupSectionRef">
            <div class="mb-2.5 text-[12px] font-bold text-[#999] tracking-widest">启动偏好</div>
            <div class="overflow-hidden rounded-[10px] border border-[#e7e7e7] bg-white divide-y divide-[#ececec]">
              <div class="px-3.5 py-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">启动后自动开启实时获取</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">进入聊天页后自动打开“实时开关”</div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="desktopAutoRealtime"
                    class="settings-switch shrink-0"
                    :class="switchTrackClass(desktopAutoRealtime)"
                    @click="toggleDesktopAutoRealtime"
                  >
                    <span class="settings-switch-thumb" :class="desktopAutoRealtime ? 'translate-x-[20px]' : 'translate-x-0'" />
                  </button>
                </div>
              </div>

              <div class="px-3.5 py-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">有数据时默认进入聊天页</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">有已解密账号时，打开应用跳转到 /chat</div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="desktopDefaultToChatWhenData"
                    class="settings-switch shrink-0"
                    :class="switchTrackClass(desktopDefaultToChatWhenData)"
                    @click="toggleDesktopDefaultToChat"
                  >
                    <span class="settings-switch-thumb" :class="desktopDefaultToChatWhenData ? 'translate-x-[20px]' : 'translate-x-0'" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section ref="updatesSectionRef">
            <div class="mb-2.5 text-[12px] font-bold text-[#999] tracking-widest">更新</div>
            <div class="overflow-hidden rounded-[10px] border border-[#e7e7e7] bg-white divide-y divide-[#ececec]">
              <div class="px-3.5 py-3">
                <div class="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:justify-between">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">当前版本</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">{{ desktopVersionText }}</div>
                  </div>
                  <button
                    type="button"
                    class="shrink-0 rounded-[6px] border border-[#e2e2e2] bg-[#fafafa] px-2.5 py-1 text-[12px] text-[#222] transition hover:bg-[#f0f0f0] disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="!isDesktopEnv || desktopUpdate.manualCheckLoading.value"
                    @click="onDesktopCheckUpdates"
                  >
                    {{ desktopUpdate.manualCheckLoading.value ? '检查中...' : '检查桌面版更新' }}
                  </button>
                </div>
                <div v-if="desktopUpdate.lastCheckMessage.value" class="mt-2 rounded-[6px] bg-[#f9f9f9] border border-[#eee] px-2.5 py-1.5 text-[11px] text-[#666] whitespace-pre-wrap break-words">
                  {{ desktopUpdate.lastCheckMessage.value }}
                </div>
              </div>
            </div>
          </section>

          <section ref="snsSectionRef">
            <div class="mb-2.5 text-[12px] font-bold text-[#999] tracking-widest">朋友圈</div>
            <div class="overflow-hidden rounded-[10px] border border-[#e7e7e7] bg-white divide-y divide-[#ececec]">
              <div class="px-3.5 py-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="text-[13px] font-medium text-[#222]">朋友圈图片使用缓存</div>
                    <div class="mt-0.5 text-[11px] text-[#909090]">开启：下载解密失败时回退本地缓存（默认）；关闭：始终重新下载</div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="snsUseCache"
                    class="settings-switch shrink-0"
                    :class="switchTrackClass(snsUseCache)"
                    @click="toggleSnsUseCache"
                  >
                    <span class="settings-switch-thumb" :class="snsUseCache ? 'translate-x-[20px]' : 'translate-x-0'" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section ref="nasSectionRef">
            <div class="mb-2.5 text-[12px] font-bold text-[#999] tracking-widest">NAS 存储</div>
            <div class="overflow-hidden rounded-[10px] border border-[#e7e7e7] bg-white divide-y divide-[#ececec]">
              <div class="px-3.5 py-3">
                <div class="flex items-center gap-2 mb-3">
                  <div class="w-2 h-2 rounded-full" :class="nasConnected ? 'bg-[#07C160]' : 'bg-[#d0d0d0]'"></div>
                  <span class="text-[12px]" :class="nasConnected ? 'text-[#07C160]' : 'text-[#909090]'">
                    {{ nasConnected ? '已连接' : '未连接' }}
                  </span>
                  <span v-if="nasStatusMessage" class="text-[11px] text-[#909090]">{{ nasStatusMessage }}</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label class="block text-[11px] font-medium text-[#666] mb-1">NAS 地址</label>
                    <input
                      v-model="nasAddress"
                      type="text"
                      placeholder="zzqaa217.x3322.net"
                      class="w-full rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30 font-mono"
                      :disabled="nasConnecting"
                    />
                  </div>
                  <div>
                    <label class="block text-[11px] font-medium text-[#666] mb-1">远程路径</label>
                    <input
                      v-model="nasRemotePath"
                      type="text"
                      placeholder="/vol1/1000/备份/微信/zzqaa217"
                      class="w-full rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30 font-mono"
                      :disabled="nasConnecting"
                    />
                  </div>
                  <div>
                    <label class="block text-[11px] font-medium text-[#666] mb-1">用户名</label>
                    <input
                      v-model="nasUsername"
                      type="text"
                      placeholder="username"
                      class="w-full rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30 font-mono"
                      :disabled="nasConnecting"
                    />
                  </div>
                  <div>
                    <label class="block text-[11px] font-medium text-[#666] mb-1">密码</label>
                    <input
                      v-model="nasPassword"
                      type="password"
                      placeholder="password"
                      class="w-full rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#333] outline-none transition focus:border-[#07b75b] focus:ring-1 focus:ring-[#07b75b]/30 font-mono"
                      :disabled="nasConnecting"
                    />
                  </div>
                </div>

                <div class="mt-3 flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    class="rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="nasConnecting || !nasAddress.trim()"
                    @click="onNasConnect"
                  >
                    {{ nasConnecting ? '连接中...' : (nasConnected ? '重新连接' : '连接测试') }}
                  </button>
                  <button
                    v-if="nasConnected"
                    type="button"
                    class="rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="nasConnecting"
                    @click="onNasDisconnect"
                  >
                    断开
                  </button>
                  <button
                    v-if="nasConnected && nasFullPath"
                    type="button"
                    class="rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#222] transition hover:bg-[#f9f9f9]"
                    @click="onNasRefreshStatus"
                  >
                    刷新状态
                  </button>
                </div>

                <div v-if="nasFullPath" class="mt-2 text-[11px] text-[#909090] break-all">
                  完整路径：{{ nasFullPath }}
                </div>
                <div v-if="nasError" class="mt-1.5 text-[11px] text-red-600 whitespace-pre-wrap">{{ nasError }}</div>
                <div v-if="nasMessage" class="mt-1.5 text-[11px] text-[#1b6b43] whitespace-pre-wrap">{{ nasMessage }}</div>
              </div>

              <div class="px-3.5 py-3">
                <div class="text-[13px] font-medium text-[#222] mb-2.5">增量同步</div>

                <div class="flex items-center justify-between gap-3 mb-2">
                  <div class="min-w-0 flex-1">
                    <div class="text-[12px] font-medium text-[#222]">启动后自动同步</div>
                    <div class="text-[10px] text-[#909090]">打开应用后自动同步一次数据库到 NAS</div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="nasAutoStartupSync"
                    class="settings-switch shrink-0"
                    :class="switchTrackClass(nasAutoStartupSync)"
                    @click="nasAutoStartupSync = !nasAutoStartupSync; onNasAutoSyncChange()"
                  >
                    <span class="settings-switch-thumb" :class="nasAutoStartupSync ? 'translate-x-[20px]' : 'translate-x-0'" />
                  </button>
                </div>

                <div class="flex items-center justify-between gap-3 mb-2">
                  <div class="min-w-0 flex-1">
                    <div class="text-[12px] font-medium text-[#222]">实时数据自动同步</div>
                    <div class="text-[10px] text-[#909090]">实时获取到新消息后自动同步到 NAS</div>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="nasAutoRealtimeSync"
                    class="settings-switch shrink-0"
                    :class="switchTrackClass(nasAutoRealtimeSync)"
                    @click="nasAutoRealtimeSync = !nasAutoRealtimeSync; onNasAutoSyncChange()"
                  >
                    <span class="settings-switch-thumb" :class="nasAutoRealtimeSync ? 'translate-x-[20px]' : 'translate-x-0'" />
                  </button>
                </div>

                <div class="flex flex-wrap items-center gap-2 mt-3 mb-2">
                  <button
                    type="button"
                    class="rounded-[6px] border border-[#e2e2e2] bg-white px-2.5 py-1.5 text-[12px] text-[#222] transition hover:bg-[#f9f9f9] disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="!nasConnected || nasSyncing"
                    @click="onNasCheckStatus"
                  >
                    检查状态
                  </button>
                  <button
                    type="button"
                    class="rounded-[6px] bg-[#07C160] px-2.5 py-1.5 text-[12px] text-white transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="!nasConnected || nasSyncing"
                    @click="onNasSyncNow"
                  >
                    同步{{ nasSyncAccountLabel ? ` (${nasSyncAccountLabel})` : '' }}
                  </button>
                  <button
                    v-if="nasSyncing"
                    type="button"
                    class="rounded-[6px] border border-red-300 bg-white px-2.5 py-1.5 text-[12px] text-red-600 transition hover:bg-red-50"
                    @click="onNasSyncCancel"
                  >
                    停止同步
                  </button>
                </div>

                <div v-if="nasSyncMessage" class="text-[11px] text-[#1b6b43] mb-1.5">{{ nasSyncMessage }}</div>
                <div v-if="nasSyncError" class="text-[11px] text-red-600 mb-1.5">{{ nasSyncError }}</div>

                <div v-if="nasSyncing" class="mt-2">
                  <div class="flex items-center justify-between gap-3 text-[11px] text-[#555]">
                    <div class="min-w-0 truncate">{{ nasSyncProgressText }}</div>
                    <div class="shrink-0 tabular-nums" v-if="nasSyncTotal > 0">{{ nasSyncCurrent }}/{{ nasSyncTotal }}</div>
                  </div>
                  <div class="mt-1.5 h-2 overflow-hidden rounded-full bg-[#e8e8e8]">
                    <div
                      class="h-full rounded-full bg-[#07C160] transition-[width] duration-200 ease-out"
                      :class="nasSyncIndeterminate ? 'animate-pulse' : ''"
                      :style="{ width: nasSyncBarWidth }"
                    />
                  </div>
                  <div v-if="nasSyncCurrentFile" class="mt-1 text-[10px] text-[#909090] break-all">{{ nasSyncCurrentFile }}</div>
                </div>
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { DESKTOP_SETTING_AUTO_REALTIME_KEY, DESKTOP_SETTING_DEFAULT_TO_CHAT_KEY, SNS_SETTING_USE_CACHE_KEY, readLocalBoolSetting, writeLocalBoolSetting } from '~/lib/desktop-settings'
import { readApiBaseOverride, writeApiBaseOverride } from '~/lib/api-settings'
import { invalidateApiBaseCache } from '~/composables/useApiBase'
import { reportServerErrorFromError } from '~/lib/server-error-logging'
import { useChatAccountsStore } from '~/stores/chatAccounts'
import { storeToRefs } from 'pinia'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const settingNavItems = [
  { key: 'desktop', label: '桌面行为', hint: '启动 / 关闭 / 端口' },
  { key: 'startup', label: '启动偏好', hint: '自动实时 / 默认页面' },
  { key: 'updates', label: '更新', hint: '版本信息 / 检查更新' },
          { key: 'sns', label: '朋友圈', hint: '图片缓存策略' },
          { key: 'nas', label: 'NAS 存储', hint: '网络存储 / 远程目录' },
        ]

const activeSection = ref(settingNavItems[0].key)
const contentScrollRef = ref(null)
const desktopSectionRef = ref(null)
const startupSectionRef = ref(null)
const updatesSectionRef = ref(null)
const snsSectionRef = ref(null)
const nasSectionRef = ref(null)

const isDesktopEnv = ref(false)
const desktopUpdate = useDesktopUpdate()

const desktopVersionText = computed(() => {
  if (!isDesktopEnv.value) return '仅桌面端可用'
  const v = String(desktopUpdate.currentVersion.value || '').trim()
  return v || '—'
})

const desktopAutoRealtime = ref(false)
const desktopDefaultToChatWhenData = ref(false)
const snsUseCache = ref(true)

const desktopAutoLaunch = ref(false)
const desktopAutoLaunchLoading = ref(false)
const desktopAutoLaunchError = ref('')

const desktopCloseBehavior = ref('tray')
const desktopCloseBehaviorLoading = ref(false)
const desktopCloseBehaviorError = ref('')

const desktopBackendPortInput = ref('')
const desktopBackendPortLoading = ref(false)
const desktopBackendPortApplying = ref(false)
const desktopBackendPortError = ref('')
const desktopBackendPortDefault = ref(10392)

const desktopOutputDir = ref('')
const desktopOutputDirDefault = ref('')
const desktopOutputDirInput = ref('')
const desktopOutputDirPending = ref('')
const desktopOutputDirLoading = ref(false)
const desktopOutputDirApplying = ref(false)
const desktopOutputDirError = ref('')
const desktopOutputDirMessage = ref('')
const desktopOutputDirIsDefault = ref(true)
const desktopOutputDirCanChange = ref(true)
const desktopOutputDirUnavailableReason = ref('')
const desktopOutputDirProgress = ref(null)
let removeDesktopOutputDirProgressListener = null
const desktopOutputDirText = computed(() => {
  if (!isDesktopEnv.value) return '仅桌面端可用'
  const v = String(desktopOutputDir.value || '').trim()
  return v || '—'
})
const desktopOutputDirDefaultText = computed(() => {
  if (!isDesktopEnv.value) return '仅桌面端可用'
  const v = String(desktopOutputDirDefault.value || '').trim()
  return v || '—'
})
const desktopOutputDirPendingText = computed(() => {
  const v = String(desktopOutputDirPending.value || '').trim()
  return v || ''
})
const desktopOutputDirProgressPercent = computed(() => {
  const n = Number(desktopOutputDirProgress.value?.percent || 0)
  if (!Number.isFinite(n) || n < 0) return 0
  return Math.max(0, Math.min(100, Math.round(n)))
})
const desktopOutputDirProgressPercentText = computed(() => `${desktopOutputDirProgressPercent.value}%`)
const desktopOutputDirProgressText = computed(() => {
  const text = String(desktopOutputDirProgress.value?.message || '').trim()
  return text || '正在迁移 output 目录'
})
const desktopOutputDirProgressIndeterminate = computed(() => {
  const stage = String(desktopOutputDirProgress.value?.stage || '').trim()
  return stage === 'preparing' || stage === 'scanning' || stage === 'rolling-back' || stage === 'restarting'
})
const desktopOutputDirProgressBarWidth = computed(() => {
  if (!desktopOutputDirProgress.value) return '0%'
  if (desktopOutputDirProgressIndeterminate.value) return '28%'
  return `${Math.max(6, desktopOutputDirProgressPercent.value)}%`
})
const desktopOutputDirProgressDetail = computed(() => {
  const progress = desktopOutputDirProgress.value
  if (!progress) return ''

  const parts = []
  const bytesTotal = Number(progress.bytesTotal || 0)
  const bytesTransferred = Number(progress.bytesTransferred || 0)
  const itemsTotal = Number(progress.itemsTotal || 0)
  const itemsTransferred = Number(progress.itemsTransferred || 0)

  if (bytesTotal > 0) {
    parts.push(`${formatBytes(bytesTransferred)} / ${formatBytes(bytesTotal)}`)
  } else if (itemsTotal > 0) {
    parts.push(`${Math.min(itemsTransferred, itemsTotal)} / ${itemsTotal} 项`)
  }

  const currentFile = String(progress.currentFile || '').trim()
  if (currentFile) {
    parts.push(currentFile)
  }

  return parts.join(' · ')
})
const desktopOutputDirControlsDisabled = computed(() => (
  !isDesktopEnv.value || !desktopOutputDirCanChange.value || desktopOutputDirLoading.value || desktopOutputDirApplying.value
))

const desktopLogFilePath = ref('')
const desktopLogFileLoading = ref(false)
const desktopLogFileOpening = ref(false)
const desktopLogFileError = ref('')
const desktopLogFileText = computed(() => {
  const v = String(desktopLogFilePath.value || '').trim()
  return v || '—'
})

const switchTrackClass = (enabled, disabled = false) => {
  if (disabled) return enabled ? 'bg-[#07b75b] opacity-50 cursor-not-allowed' : 'bg-[#d0d0d0] opacity-50 cursor-not-allowed'
  return enabled ? 'bg-[#07b75b] hover:brightness-95' : 'bg-[#d0d0d0] hover:brightness-95'
}

const formatBytes = (value) => {
  const n = Number(value || 0)
  if (!Number.isFinite(n) || n <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let next = n
  let unitIndex = 0
  while (next >= 1024 && unitIndex < units.length - 1) {
    next /= 1024
    unitIndex += 1
  }
  const digits = next >= 100 || unitIndex === 0 ? 0 : next >= 10 ? 1 : 2
  return `${next.toFixed(digits)} ${units[unitIndex]}`
}

const applyDesktopOutputDirProgress = (progress) => {
  if (!progress || progress.active === false) {
    desktopOutputDirProgress.value = null
    return
  }
  desktopOutputDirProgress.value = { ...progress }
}

const refreshDesktopOutputDirProgress = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.getOutputDirChangeProgress) return
  try {
    const progress = await window.wechatDesktop.getOutputDirChangeProgress()
    applyDesktopOutputDirProgress(progress)
  } catch {}
}

const sectionElements = computed(() => [
  { key: 'desktop', el: desktopSectionRef.value },
  { key: 'startup', el: startupSectionRef.value },
  { key: 'updates', el: updatesSectionRef.value },
          { key: 'sns', el: snsSectionRef.value },
          { key: 'nas', el: nasSectionRef.value },
        ])

const scrollToSection = (key) => {
  const scrollHost = contentScrollRef.value
  const target = sectionElements.value.find((item) => item.key === key)?.el
  activeSection.value = key
  if (!scrollHost || !target) return
  scrollHost.scrollTo({
    top: Math.max(0, target.offsetTop - 10),
    behavior: 'smooth',
  })
}

const onContentScroll = () => {
  const scrollHost = contentScrollRef.value
  if (!scrollHost) return
  const position = scrollHost.scrollTop + 120
  let current = settingNavItems[0].key
  for (const section of sectionElements.value) {
    if (!section.el) continue
    if (section.el.offsetTop <= position) current = section.key
  }
  activeSection.value = current
}

const handleClose = () => {
  emit('close')
}

const onEscKeydown = (event) => {
  if (event?.key !== 'Escape') return
  event.preventDefault()
  handleClose()
}

const fetchAdminEndpoint = async (url, options = {}) => {
  const apiBase = useApiBase()
  try {
    return await $fetch(url, {
      baseURL: apiBase,
      ...options,
    })
  } catch (e) {
    await reportServerErrorFromError(e, {
      method: options?.method || 'GET',
      requestUrl: url,
      source: 'SettingsDialog',
      apiBase,
    })
    throw e
  }
}

const refreshDesktopAutoLaunch = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.getAutoLaunch) return
  desktopAutoLaunchLoading.value = true
  desktopAutoLaunchError.value = ''
  try {
    desktopAutoLaunch.value = !!(await window.wechatDesktop.getAutoLaunch())
  } catch (e) {
    desktopAutoLaunchError.value = e?.message || '读取开机自启动状态失败'
  } finally {
    desktopAutoLaunchLoading.value = false
  }
}

const setDesktopAutoLaunch = async (enabled) => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.setAutoLaunch) return
  desktopAutoLaunchLoading.value = true
  desktopAutoLaunchError.value = ''
  try {
    desktopAutoLaunch.value = !!(await window.wechatDesktop.setAutoLaunch(!!enabled))
  } catch (e) {
    desktopAutoLaunchError.value = e?.message || '设置开机自启动失败'
    await refreshDesktopAutoLaunch()
  } finally {
    desktopAutoLaunchLoading.value = false
  }
}

const refreshDesktopCloseBehavior = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.getCloseBehavior) return
  desktopCloseBehaviorLoading.value = true
  desktopCloseBehaviorError.value = ''
  try {
    const v = await window.wechatDesktop.getCloseBehavior()
    desktopCloseBehavior.value = String(v || '').toLowerCase() === 'exit' ? 'exit' : 'tray'
  } catch (e) {
    desktopCloseBehaviorError.value = e?.message || '读取关闭窗口行为失败'
  } finally {
    desktopCloseBehaviorLoading.value = false
  }
}

const setDesktopCloseBehavior = async (behavior) => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.setCloseBehavior) return
  const desired = String(behavior || '').toLowerCase() === 'exit' ? 'exit' : 'tray'
  desktopCloseBehaviorLoading.value = true
  desktopCloseBehaviorError.value = ''
  try {
    const v = await window.wechatDesktop.setCloseBehavior(desired)
    desktopCloseBehavior.value = String(v || '').toLowerCase() === 'exit' ? 'exit' : 'tray'
  } catch (e) {
    desktopCloseBehaviorError.value = e?.message || '设置关闭窗口行为失败'
    await refreshDesktopCloseBehavior()
  } finally {
    desktopCloseBehaviorLoading.value = false
  }
}

const refreshDesktopBackendPort = async () => {
  if (!process.client || typeof window === 'undefined') return
  desktopBackendPortLoading.value = true
  desktopBackendPortError.value = ''
  try {
    if (window.wechatDesktop?.getBackendPort) {
      const v = await window.wechatDesktop.getBackendPort()
      const n = Number(v)
      if (Number.isInteger(n) && n >= 1 && n <= 65535) {
        desktopBackendPortInput.value = String(n)
        return
      }
    }

    try {
      const resp = await fetchAdminEndpoint('/admin/port')
      const n = Number(resp?.port)
      const d = Number(resp?.default_port)
      if (Number.isInteger(d) && d >= 1 && d <= 65535) desktopBackendPortDefault.value = d
      if (Number.isInteger(n) && n >= 1 && n <= 65535) {
        desktopBackendPortInput.value = String(n)
        return
      }
    } catch {}

    let detectedPort = null
    const override = readApiBaseOverride()
    if (override && /^https?:\/\//i.test(override)) {
      try {
        const u = new URL(override)
        const n = Number(u.port)
        if (Number.isInteger(n) && n >= 1 && n <= 65535) detectedPort = n
      } catch {}
    }
    if (!desktopBackendPortInput.value) desktopBackendPortInput.value = String(detectedPort ?? 10392)
  } catch (e) {
    desktopBackendPortError.value = e?.message || '读取后端端口失败'
  } finally {
    desktopBackendPortLoading.value = false
  }
}

const refreshDesktopOutputDir = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.getOutputDir && !window.wechatDesktop?.getOutputDirInfo) return
  desktopOutputDirLoading.value = true
  desktopOutputDirError.value = ''
  try {
    if (window.wechatDesktop?.getOutputDirInfo) {
      const info = await window.wechatDesktop.getOutputDirInfo()
      desktopOutputDir.value = String(info?.path || '').trim()
      desktopOutputDirDefault.value = String(info?.defaultPath || '').trim()
      desktopOutputDirPending.value = String(info?.pendingPath || '').trim()
      desktopOutputDirIsDefault.value = !!info?.isDefault
      desktopOutputDirCanChange.value = info?.canChange !== false
      desktopOutputDirUnavailableReason.value = String(info?.changeUnavailableReason || '').trim()
      desktopOutputDirInput.value = desktopOutputDir.value || desktopOutputDirDefault.value
      if (info?.lastError) {
        desktopOutputDirError.value = String(info.lastError || '').trim()
      }
      return
    }

    const v = await window.wechatDesktop.getOutputDir()
    desktopOutputDir.value = String(v || '').trim()
    desktopOutputDirDefault.value = desktopOutputDir.value
    desktopOutputDirPending.value = ''
    desktopOutputDirIsDefault.value = true
    desktopOutputDirCanChange.value = false
    desktopOutputDirUnavailableReason.value = '当前桌面环境不支持修改 output 目录'
    desktopOutputDirInput.value = desktopOutputDir.value
  } catch (e) {
    desktopOutputDirError.value = e?.message || '读取 output 目录失败'
  } finally {
    desktopOutputDirLoading.value = false
  }
}

const onDesktopOpenOutputDir = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.openOutputDir) return
  desktopOutputDirLoading.value = true
  desktopOutputDirError.value = ''
  try {
    const res = await window.wechatDesktop.openOutputDir()
    if (res?.path) desktopOutputDir.value = String(res.path || '').trim()
  } catch (e) {
    desktopOutputDirError.value = e?.message || '打开 output 目录失败'
  } finally {
    desktopOutputDirLoading.value = false
  }
}

const onDesktopChooseOutputDir = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.chooseDirectory) return
  desktopOutputDirError.value = ''
  desktopOutputDirMessage.value = ''
  try {
    const result = await window.wechatDesktop.chooseDirectory({ title: '选择新的 output 目录' })
    if (result && !result.canceled && Array.isArray(result.filePaths) && result.filePaths.length > 0) {
      desktopOutputDirInput.value = String(result.filePaths[0] || '').trim()
    }
  } catch (e) {
    desktopOutputDirError.value = e?.message || '选择 output 目录失败'
  }
}

const applyDesktopOutputDir = async (nextDir) => {
  if (!process.client || typeof window === 'undefined') return
  if (!window.wechatDesktop?.setOutputDir) {
    desktopOutputDirError.value = '当前桌面环境不支持修改 output 目录'
    return
  }
  if (!desktopOutputDirCanChange.value) {
    desktopOutputDirError.value = desktopOutputDirUnavailableReason.value || '当前环境不支持修改 output 目录'
    return
  }
  desktopOutputDirApplying.value = true
  desktopOutputDirError.value = ''
  desktopOutputDirMessage.value = ''
  desktopOutputDirProgress.value = null
  try {
    const res = await window.wechatDesktop.setOutputDir(String(nextDir ?? '').trim())
    if (res?.success === false) {
      desktopOutputDirError.value = String(res?.error || '修改 output 目录失败').trim()
      await refreshDesktopOutputDir()
      return
    }
    await refreshDesktopOutputDir()
    desktopOutputDirMessage.value = String(
      res?.message || (res?.changed === false ? 'output 目录未变化' : 'output 目录已更新')
    ).trim()
  } catch (e) {
    desktopOutputDirError.value = e?.message || '修改 output 目录失败'
    await refreshDesktopOutputDir()
  } finally {
    desktopOutputDirApplying.value = false
  }
}

const onDesktopOutputDirApply = async () => {
  await applyDesktopOutputDir(desktopOutputDirInput.value)
}

const onDesktopOutputDirReset = async () => {
  desktopOutputDirInput.value = desktopOutputDirDefault.value
  await applyDesktopOutputDir('')
}

const refreshBackendLogFileInfo = async () => {
  if (!process.client || typeof window === 'undefined') return
  desktopLogFileLoading.value = true
  desktopLogFileError.value = ''
  try {
    const resp = await fetchAdminEndpoint('/admin/log-file')
    desktopLogFilePath.value = String(resp?.path || '').trim()
  } catch (e) {
    desktopLogFileError.value = e?.message || '读取日志文件失败'
  } finally {
    desktopLogFileLoading.value = false
  }
}

const onOpenBackendLogFile = async () => {
  if (!process.client || typeof window === 'undefined') return
  desktopLogFileOpening.value = true
  desktopLogFileError.value = ''
  try {
    const resp = await fetchAdminEndpoint('/admin/log-file/open', { method: 'POST' })
    if (resp?.path) desktopLogFilePath.value = String(resp.path || '').trim()
  } catch (e) {
    desktopLogFileError.value = e?.message || '打开日志文件失败'
  } finally {
    desktopLogFileOpening.value = false
  }
}

const applyDesktopBackendPort = async () => {
  if (!process.client || typeof window === 'undefined') return
  const raw = String(desktopBackendPortInput.value || '').trim()
  const n = Number(raw)
  if (!Number.isInteger(n) || n < 1 || n > 65535) {
    desktopBackendPortError.value = '端口无效：请输入 1-65535 的整数'
    return
  }
  desktopBackendPortApplying.value = true
  desktopBackendPortError.value = ''
  try {
    if (window.wechatDesktop?.setBackendPort) {
      await window.wechatDesktop.setBackendPort(n)
      return
    }

    let currentBackendPort = null
    try {
      const info = await fetchAdminEndpoint('/admin/port')
      const p = Number(info?.port)
      if (Number.isInteger(p) && p >= 1 && p <= 65535) currentBackendPort = p
    } catch {}
    const uiPort = (() => {
      const rawPort = String(window.location?.port || '').trim()
      if (rawPort) return Number(rawPort)
      return window.location?.protocol === 'https:' ? 443 : 80
    })()
    const isUiServedByBackend = !!(currentBackendPort && uiPort === currentBackendPort)

    await fetchAdminEndpoint('/admin/port', {
      method: 'POST',
      body: { port: n },
    })

    let protocol = String(window.location?.protocol || 'http:')
    if (protocol !== 'http:' && protocol !== 'https:') protocol = 'http:'
    const host = String(window.location?.hostname || '').trim() || '127.0.0.1'
    const nextOrigin = `${protocol}//${host}:${n}`
    writeApiBaseOverride(`${nextOrigin}/api`)
    invalidateApiBaseCache()

    const waitForHealth = async (healthUrl, timeoutMs = 30_000) => {
      const startedAt = Date.now()
      while (true) {
        try {
          const r = await fetch(healthUrl, { method: 'GET' })
          if (r && r.status < 500) return
        } catch {}
        if (Date.now() - startedAt > timeoutMs) throw new Error(`后端启动超时：${healthUrl}`)
        await new Promise((r) => setTimeout(r, 300))
      }
    }
    await waitForHealth(`${nextOrigin}/api/health`, 30_000)

    if (isUiServedByBackend) {
      const nextUrl = new URL(window.location.href)
      nextUrl.port = String(n)
      window.location.href = nextUrl.toString()
      return
    }

    try {
      window.location.reload()
    } catch {}
  } catch (e) {
    desktopBackendPortError.value = e?.message || '设置后端端口失败（若为网页端，请确认后端为本机启动且允许重启）'
    await refreshDesktopBackendPort()
  } finally {
    desktopBackendPortApplying.value = false
  }
}

const toggleDesktopAutoLaunch = async () => {
  if (!isDesktopEnv.value || desktopAutoLaunchLoading.value) return
  await setDesktopAutoLaunch(!desktopAutoLaunch.value)
}

const onDesktopCloseBehaviorChange = async (ev) => {
  const v = String(ev?.target?.value || '').trim()
  await setDesktopCloseBehavior(v)
}

const onDesktopBackendPortApply = async () => {
  await applyDesktopBackendPort()
}

const onDesktopBackendPortReset = async () => {
  desktopBackendPortInput.value = String(desktopBackendPortDefault.value || 10392)
  await applyDesktopBackendPort()
}

const toggleDesktopAutoRealtime = () => {
  const next = !desktopAutoRealtime.value
  desktopAutoRealtime.value = next
  writeLocalBoolSetting(DESKTOP_SETTING_AUTO_REALTIME_KEY, next)
}

const toggleDesktopDefaultToChat = () => {
  const next = !desktopDefaultToChatWhenData.value
  desktopDefaultToChatWhenData.value = next
  writeLocalBoolSetting(DESKTOP_SETTING_DEFAULT_TO_CHAT_KEY, next)
}

const toggleSnsUseCache = () => {
  const next = !snsUseCache.value
  snsUseCache.value = next
  writeLocalBoolSetting(SNS_SETTING_USE_CACHE_KEY, next)
}

// --- NAS 存储 ---
const nasAddress = ref('zzqaa217.x3322.net')
const nasUsername = ref('zzqaa217')
const nasPassword = ref('zhang217')
const nasRemotePath = ref('/vol1/1000/备份/微信/zzqaa217')
const nasConnected = ref(false)
const nasFullPath = ref('')
const nasMountPath = ref('')
const nasConnecting = ref(false)
const nasSettingOutput = ref(false)
const nasStatusMessage = ref('')
const nasError = ref('')
const nasMessage = ref('')

const refreshNasStatus = async () => {
  if (!process.client || typeof window === 'undefined') return
  nasError.value = ''
  nasStatusMessage.value = ''
  try {
    const res = await fetchAdminEndpoint('/api/nas/status')
    nasConnected.value = !!res?.connected
    nasFullPath.value = String(res?.path || '').trim()
    nasMountPath.value = String(res?.mount || '').trim()
    if (res?.config) {
      if (!nasAddress.value) nasAddress.value = String(res.config.address || '')
      if (!nasUsername.value) nasUsername.value = String(res.config.username || '')
      if (!nasRemotePath.value) nasRemotePath.value = String(res.config.remote_path || '')
    }
    if (nasConnected.value) {
      nasStatusMessage.value = '已连接'
    } else if (nasAddress.value.trim()) {
      await onNasConnect()
    }
  } catch (e) {
    nasError.value = e?.message || '获取 NAS 状态失败'
  }
}

const onNasConnect = async () => {
  if (!process.client || typeof window === 'undefined') return
  const addr = String(nasAddress.value || '').trim()
  if (!addr) {
    nasError.value = '请输入 NAS 地址'
    return
  }
  nasConnecting.value = true
  nasError.value = ''
  nasMessage.value = ''
  try {
    const res = await fetchAdminEndpoint('/api/nas/connect', {
      method: 'POST',
      body: {
        address: addr,
        username: String(nasUsername.value || '').trim(),
        password: nasPassword.value,
        remote_path: String(nasRemotePath.value || '').trim(),
      },
    })
    if (res?.success) {
      nasConnected.value = true
      nasFullPath.value = String(res.path || '')
      nasMountPath.value = String(res.mount || '')
      nasMessage.value = '连接成功'
    }
  } catch (e) {
    nasError.value = e?.data?.detail || e?.message || '连接 NAS 失败'
  } finally {
    nasConnecting.value = false
  }
}

const onNasDisconnect = async () => {
  if (!process.client || typeof window === 'undefined') return
  nasConnecting.value = true
  nasError.value = ''
  nasMessage.value = ''
  try {
    await fetchAdminEndpoint('/api/nas/disconnect', { method: 'POST' })
    nasConnected.value = false
    nasMessage.value = '已断开'
  } catch (e) {
    nasError.value = e?.data?.detail || e?.message || '断开 NAS 失败'
  } finally {
    nasConnecting.value = false
  }
}

const onNasRefreshStatus = async () => {
  await refreshNasStatus()
}

const onNasSetOutput = async () => {
  if (!process.client || typeof window === 'undefined') return
  const targetPath = nasMountPath.value || nasFullPath.value
  if (!targetPath) {
    nasError.value = '没有可用的 NAS 路径'
    return
  }
  nasSettingOutput.value = true
  nasError.value = ''
  nasMessage.value = ''
  try {
    const res = await fetchAdminEndpoint('/api/nas/set-output', {
      method: 'POST',
      body: { path: targetPath },
    })
    if (res?.success) {
      nasMessage.value = `output 目录已设为: ${res.path}`
    }
  } catch (e) {
    nasError.value = e?.data?.detail || e?.message || '设置 output 目录失败'
  } finally {
    nasSettingOutput.value = false
  }
}

// --- NAS 同步 ---
const nasAutoStartupSync = ref(false)
const nasAutoRealtimeSync = ref(false)
const nasSyncing = ref(false)
const nasSyncStage = ref('')
const nasSyncTotal = ref(0)
const nasSyncCurrent = ref(0)
const nasSyncCurrentFile = ref('')
const nasSyncMessage = ref('')
const nasSyncError = ref('')
let nasSyncPollTimer = null

const chatAccountsStore = useChatAccountsStore()
const { selectedAccount } = storeToRefs(chatAccountsStore)
const nasSyncAccountLabel = computed(() => {
  return String(selectedAccount.value || '').trim() || ''
})

const nasSyncProgressText = computed(() => {
  if (!nasSyncing.value) return ''
  if (nasSyncStage.value === 'scanning' || nasSyncStage.value === 'starting') return '正在扫描文件...'
  if (nasSyncStage.value === 'syncing' && nasSyncTotal.value > 0) {
    return `正在同步 (${nasSyncCurrent.value}/${nasSyncTotal.value})`
  }
  return nasSyncMessage.value || '同步中...'
})

const nasSyncIndeterminate = computed(() => {
  return nasSyncStage.value === 'scanning' || nasSyncStage.value === 'starting' || nasSyncTotal.value === 0
})

const nasSyncBarWidth = computed(() => {
  if (!nasSyncing.value) return '0%'
  if (nasSyncIndeterminate.value) return '28%'
  if (nasSyncTotal.value > 0) {
    const pct = Math.round((nasSyncCurrent.value / nasSyncTotal.value) * 100)
    return `${Math.max(6, Math.min(100, pct))}%`
  }
  return '28%'
})

const loadNasAutoSyncConfig = async () => {
  if (!process.client || typeof window === 'undefined') return
  try {
    const res = await fetchAdminEndpoint('/api/nas/auto-sync')
    nasAutoStartupSync.value = !!res?.startup_auto_sync
    nasAutoRealtimeSync.value = !!res?.realtime_auto_sync
  } catch {}
}

const onNasAutoSyncChange = async () => {
  if (!process.client || typeof window === 'undefined') return
  try {
    await fetchAdminEndpoint('/api/nas/auto-sync', {
      method: 'POST',
      body: {
        startup_auto_sync: nasAutoStartupSync.value,
        realtime_auto_sync: nasAutoRealtimeSync.value,
      },
    })
  } catch {}
}

const stopNasSyncPolling = () => {
  if (nasSyncPollTimer) {
    clearInterval(nasSyncPollTimer)
    nasSyncPollTimer = null
  }
}

const pollNasSyncStatus = async () => {
  if (!process.client || typeof window === 'undefined') return
  try {
    const res = await fetchAdminEndpoint('/api/nas/sync/status')
    const running = !!res?.running
    nasSyncing.value = running
    nasSyncStage.value = String(res?.stage || '')
    nasSyncTotal.value = Number(res?.total || 0)
    nasSyncCurrent.value = Number(res?.current || 0)
    nasSyncCurrentFile.value = String(res?.current_file || '')
    nasSyncMessage.value = String(res?.message || '')
    nasSyncError.value = String(res?.error || '')

    if (!running && res?.completed) {
      stopNasSyncPolling()
    }
    if (!running && !res?.completed && res?.stage === 'error') {
      stopNasSyncPolling()
    }
    if (!running) {
      nasSyncing.value = false
    }
  } catch (e) {
    nasSyncError.value = e?.message || '获取同步状态失败'
    stopNasSyncPolling()
    nasSyncing.value = false
  }
}

const onNasSyncNow = async () => {
  if (!process.client || typeof window === 'undefined') return
  if (!nasConnected.value) {
    nasSyncError.value = '请先连接 NAS'
    return
  }
  nasSyncError.value = ''
  nasSyncMessage.value = ''
  nasSyncing.value = true
  nasSyncStage.value = 'starting'
  nasSyncTotal.value = 0
  nasSyncCurrent.value = 0
  nasSyncCurrentFile.value = ''

  await nextTick()
  await new Promise(r => requestAnimationFrame(() => setTimeout(r, 0)))

  const account = nasSyncAccountLabel.value

  try {
    const res = await fetchAdminEndpoint('/api/nas/sync', { method: 'POST', body: { account } })
    if (res?.success) {
      nasSyncMessage.value = res.message || '同步已启动'
      stopNasSyncPolling()
      nasSyncPollTimer = setInterval(pollNasSyncStatus, 1000)
    } else {
      nasSyncError.value = res?.detail || '启动同步失败'
    }
  } catch (e) {
    const detail = e?.data?.detail || ''
    if (detail.includes('已在运行')) {
      nasSyncMessage.value = detail
      stopNasSyncPolling()
      nasSyncPollTimer = setInterval(pollNasSyncStatus, 1000)
    } else {
      nasSyncing.value = false
      nasSyncError.value = detail || e?.message || '启动同步失败'
    }
  }
}

const onNasSyncCancel = async () => {
  if (!process.client || typeof window === 'undefined') return
  try {
    const res = await fetchAdminEndpoint('/api/nas/sync/cancel', { method: 'POST' })
    if (res?.success) {
      nasSyncMessage.value = res.message || '同步已取消'
      nasSyncing.value = false
      stopNasSyncPolling()
    } else {
      nasSyncError.value = res?.detail || '取消失败'
    }
  } catch (e) {
    nasSyncError.value = e?.data?.detail || e?.message || '取消失败'
  }
}

const onNasCheckStatus = async () => {
  await refreshNasStatus()
}

const onDesktopCheckUpdates = async () => {
  await desktopUpdate.manualCheck()
}

watch(() => props.open, async (isOpen) => {
  if (!isOpen) {
    stopNasSyncPolling()
    return
  }
  await refreshBackendLogFileInfo()
  if (isDesktopEnv.value) {
    await refreshDesktopOutputDir()
    await refreshDesktopOutputDirProgress()
  }
  await refreshNasStatus()
  await loadNasAutoSyncConfig()
  stopNasSyncPolling()
  await pollNasSyncStatus()
  if (nasSyncing.value) {
    nasSyncPollTimer = setInterval(pollNasSyncStatus, 1000)
  }
}, { immediate: true })

onMounted(async () => {
  if (process.client && typeof window !== 'undefined') {
    const isElectron = /electron/i.test(String(navigator.userAgent || ''))
    isDesktopEnv.value = isElectron && !!window.wechatDesktop
    window.addEventListener('keydown', onEscKeydown)
    if (window.wechatDesktop?.onOutputDirChangeProgress) {
      removeDesktopOutputDirProgressListener = window.wechatDesktop.onOutputDirChangeProgress((progress) => {
        applyDesktopOutputDirProgress(progress)
      })
    }
  }

  desktopAutoRealtime.value = readLocalBoolSetting(DESKTOP_SETTING_AUTO_REALTIME_KEY, false)
  desktopDefaultToChatWhenData.value = readLocalBoolSetting(DESKTOP_SETTING_DEFAULT_TO_CHAT_KEY, false)
  snsUseCache.value = readLocalBoolSetting(SNS_SETTING_USE_CACHE_KEY, true)

  await refreshDesktopBackendPort()
  if (isDesktopEnv.value) {
    void desktopUpdate.initListeners()
    await refreshDesktopAutoLaunch()
    await refreshDesktopCloseBehavior()
    await refreshDesktopOutputDir()
    await refreshDesktopOutputDirProgress()
  }

  await refreshNasStatus()
  await loadNasAutoSyncConfig()
  await nextTick()
  onContentScroll()
})

onBeforeUnmount(() => {
  if (!process.client || typeof window === 'undefined') return
  stopNasSyncPolling()
  window.removeEventListener('keydown', onEscKeydown)
  if (typeof removeDesktopOutputDirProgressListener === 'function') {
    removeDesktopOutputDirProgressListener()
    removeDesktopOutputDirProgressListener = null
  }
})
</script>

<style scoped>
.settings-switch {
  width: 44px;
  height: 24px;
  border-radius: 999px;
  padding: 2px;
  transition: background-color 0.16s ease, opacity 0.16s ease, filter 0.16s ease;
}

.settings-switch-thumb {
  display: block;
  height: 20px;
  width: 20px;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.24);
  transition: transform 0.16s ease;
}

/* 自定义右侧滚动条 */
.scrollbar-custom::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.scrollbar-custom::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-custom::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}
.scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}
</style>
