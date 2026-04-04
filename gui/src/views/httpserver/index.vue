<template>
  <div class="api-container">
    <div class="api-container-top">
      <div class="setting-item">
        <div class="setting-item-title">HOST设置</div>
        <el-input style="width: 140px" :disabled="settindDic.open" class="setting-item-input" v-model="settindDic.host" />
      </div>
      <div class="setting-item">
        <div class="setting-item-title">端口设置</div>
        <el-input style="width: 80px" :disabled="settindDic.open" class="setting-item-input" v-model="settindDic.port" />
      </div>
      <el-tag disable-transitions v-if="settindDic.open" type="success" style="margin-right: 10px">服务正在运行</el-tag>
      <el-tag disable-transitions v-else type="danger" style="margin-right: 10px">服务未运行</el-tag>
      <el-button v-if="!settindDic.open" type="primary" @click="openHttpServerAction(true)">开启</el-button>
      <el-button v-else type="danger" @click="openHttpServerAction(false)">关闭</el-button>
    </div>
    <div class="api-container-bottom">
      <div class="api-header">
        <h5 style="margin: 0">api说明</h5>
        <span class="api-copy-note">点击 URL 或 Body 可以直接复制</span>
      </div>
      <el-collapse expand-icon-position="left">
        <el-collapse-item v-for="doc in apiDocs" :key="doc.name" :title="doc.title" :name="doc.name">
          <div class="api-introduction">
            <h4>请求：</h4>
            <div class="copy-block" @click="copyText(doc.url, 'URL')">
              <code>
                <span :class="['method-tag', `method-${doc.method.toLowerCase()}`]">{{ doc.method }}</span>
                <span class="url-text">{{ doc.url }}</span>
              </code>
              <span class="copy-tip">点击复制 URL</span>
            </div>

            <template v-if="doc.body">
              <h4>Body：</h4>
              <div class="copy-block" @click="copyText(doc.body, 'Body')">
                <pre>{{ doc.body }}</pre>
                <span class="copy-tip">点击复制 Body</span>
              </div>
            </template>

            <template v-if="doc.description?.length">
              <h4>说明：</h4>
              <code class="description-block">
                <template v-for="(line, index) in doc.description" :key="index">
                  {{ line }}<br v-if="index < doc.description.length - 1" />
                </template>
              </code>
            </template>

            <template v-if="doc.response">
              <h4>返回：</h4>
              <pre class="response-block">{{ doc.response }}</pre>
            </template>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { isHttpServerRunning, openHttpServer } from '@/api/comm_tube'
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive } from 'vue'

const settindDic = reactive({
  host: '127.0.0.1',
  port: '8080',
  open: false
})

const baseUrl = computed(() => `http://${settindDic.host}:${settindDic.port}`)

const apiDocs = computed(() => [
  {
    name: '1',
    title: '获取任务列表',
    method: 'GET',
    url: `${baseUrl.value}/api/tasks`,
    description: [
      '支持 query 参数: account_id / user_id / strategy_code / task_type / platform / is_open / order_count_type',
      '返回本地任务列表，已过滤删除任务'
    ],
    response: `{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "测试任务",
      "strategy_code": "ABC123"
    }
  ]
}`
  },
  {
    name: '2',
    title: '获取任务详情',
    method: 'GET',
    url: `${baseUrl.value}/api/tasks/1`,
    description: ['按任务ID获取完整任务信息'],
    response: `{
  "code": 200,
  "data": {
    "id": 1,
    "name": "测试任务",
    "position_ratio": 1
  }
}`
  },
  {
    name: '3',
    title: '创建任务',
    method: 'POST',
    url: `${baseUrl.value}/api/tasks`,
    body: `{
  "name": "API策略任务",
  "account_id": 1,
  "platform": 10,
  "task_type": 1,
  "strategy_code": "API001",
  "order_count_type": 1,
  "position_ratio": 1
}`,
    description: [
      '字段风格与桌面端 create_task 保持一致',
      'strategy_code 不传时，task_type=1 会按现有逻辑随机生成'
    ],
    response: `{
  "code": 200,
  "message": "task created",
  "data": true
}`
  },
  {
    name: '4',
    title: '更新任务字段',
    method: 'PUT',
    url: `${baseUrl.value}/api/tasks/1`,
    body: `{
  "can_use_amount": 80000,
  "allocation_amount": 100000,
  "service_charge": 0.00025,
  "lower_limit_of_fees": 5,
  "dynamic_calculation_type": 2,
  "open_mandatory_limit_order": 1
}`,
    description: [
      '支持局部更新',
      '可直接修改 can_use_amount / allocation_amount / service_charge / lower_limit_of_fees / position_ratio 等任务字段'
    ],
    response: `{
  "code": 200,
  "message": "task updated",
  "data": {
    "id": 1
  }
}`
  },
  {
    name: '5',
    title: '启停任务',
    method: 'POST',
    url: `${baseUrl.value}/api/tasks/1/run`,
    body: `{
  "is_open": 1
}`,
    description: ['is_open: 1 开启, 0 关闭'],
    response: `{
  "code": 200,
  "message": "task running state updated",
  "data": true
}`
  },
  {
    name: '6',
    title: '调整单个任务比例',
    method: 'POST',
    url: `${baseUrl.value}/api/task/position_ratio`,
    body: `{
  "strategy_code": "API001",
  "position_ratio": 1.5
}`,
    description: [
      'task_id 与 strategy_code 二选一',
      '仅支持 order_count_type = 1 的任务'
    ],
    response: `{
  "code": 200,
  "data": {
    "task_id": 1,
    "position_ratio": 1.5
  }
}`
  },
  {
    name: '7',
    title: '获取账户资金',
    method: 'GET',
    url: `${baseUrl.value}/api/account_fund?account_id=1`,
    description: [
      '支持 account_id / task_id / strategy_code 三种定位方式',
      '如果一个都不传，则返回所有账户汇总资金'
    ],
    response: `{
  "code": 200,
  "data": {
    "cash": 100000,
    "frozen_cash": 0,
    "market_value": 50000,
    "total_asset": 150000
  }
}`
  },
  {
    name: '8',
    title: '获取本地持仓',
    method: 'GET',
    url: `${baseUrl.value}/api/tasks/1/positions`,
    description: [
      '按任务ID获取本地持仓',
      '兼容旧接口: GET /api/positions?task_id=1 或 /api/positions?strategy_code=API001'
    ],
    response: `{
  "code": 200,
  "data": [
    {
      "id": 1,
      "security_code": "600031.SH",
      "volume": 100
    }
  ]
}`
  },
  {
    name: '9',
    title: '新增持仓',
    method: 'POST',
    url: `${baseUrl.value}/api/tasks/1/positions`,
    body: `{
  "security_code": "600031",
  "volume": 100,
  "average_price": 18.23,
  "is_mock": 0
}`,
    description: [
      'security_code 支持不带后缀，接口会复用现有转换逻辑',
      'task_id 会自动按 URL 中的任务ID写入'
    ],
    response: `{
  "code": 200,
  "message": "position created",
  "data": true
}`
  },
  {
    name: '10',
    title: '批量新增持仓',
    method: 'POST',
    url: `${baseUrl.value}/api/tasks/1/positions/batch`,
    body: `[
  {
    "security_code": "600031",
    "volume": 100,
    "average_price": 18.23,
    "is_mock": 0
  },
  {
    "security_code": "000001",
    "volume": 200,
    "average_price": 12.5,
    "is_mock": 0
  }
]`,
    description: ['适合把账号持仓或一组初始化仓位一次性导入任务'],
    response: `{
  "code": 200,
  "message": "positions created",
  "data": true
}`
  },
  {
    name: '11',
    title: '获取今日成交',
    method: 'GET',
    url: `${baseUrl.value}/api/tasks/1/today_trades`,
    description: [
      '按任务ID获取今日成交',
      '兼容旧接口: GET /api/today_trades?task_id=1 或 ?strategy_code=API001'
    ],
    response: `{
  "code": 200,
  "data": [
    {
      "security_code": "600031.SH",
      "volume": 100
    }
  ]
}`
  },
  {
    name: '12',
    title: '获取远程持仓',
    method: 'GET',
    url: `${baseUrl.value}/api/tasks/1/remote_positions`,
    description: ['返回当前任务保存的远程持仓快照'],
    response: `{
  "code": 200,
  "data": [
    {
      "security_code": "600031.SH",
      "volume": 100
    }
  ]
}`
  },
  {
    name: '13',
    title: '重置远程持仓',
    method: 'DELETE',
    url: `${baseUrl.value}/api/tasks/1/remote_positions`,
    description: ['清空当前任务的远程持仓快照，不需要 Body'],
    response: `{
  "code": 200,
  "message": "remote positions reset",
  "data": true
}`
  },
  {
    name: '14',
    title: '同步远程持仓到本地账户',
    method: 'POST',
    url: `${baseUrl.value}/api/tasks/1/sync_positions`,
    description: [
      '按任务策略配置把远程持仓同步到本地账号',
      '需要对应账号已连接 QMT/交易端'
    ],
    response: `{
  "code": 200,
  "message": "positions synced",
  "data": true
}`
  },
  {
    name: '15',
    title: '一键清仓任务持仓',
    method: 'POST',
    url: `${baseUrl.value}/api/tasks/1/clear_all_stock`,
    description: ['按任务当前本地持仓逐个下卖单进行清仓'],
    response: `{
  "code": 200,
  "message": "clear all stock success",
  "data": true
}`
  }
])

onMounted(() => {
  checkHttpServer()
})

const checkHttpServer = async () => {
  const res = await isHttpServerRunning()
  settindDic.open = res
}

const fallbackCopy = (text) => {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', 'readonly')
  textarea.style.position = 'fixed'
  textarea.style.top = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

const copyText = async (text, label = '内容') => {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      fallbackCopy(text)
    }
    ElMessage.success(`${label}已复制`)
  } catch (error) {
    try {
      fallbackCopy(text)
      ElMessage.success(`${label}已复制`)
    } catch (fallbackError) {
      ElMessage.error(`${label}复制失败`)
    }
  }
}

const openHttpServerAction = (open) => {
  settindDic.open = open
  openHttpServer(open, settindDic.host, settindDic.port)
}
</script>

<style scoped lang="less">
.api-container {
  padding: 10px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;

  .api-container-top {
    display: flex;
    align-items: center;
    background: #fff;
    margin-bottom: 10px;
    padding: 8px;

    .setting-item {
      display: flex;
      align-items: center;
      margin-right: 10px;

      .setting-item-title {
        width: 80px;
        margin-right: 10px;
      }

      .setting-item-input {
        width: 100px;
      }
    }
  }

  .api-container-bottom {
    padding: 10px;
    background: #fff;
    overflow-y: auto;
  }
}

.api-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.api-copy-note {
  color: #8a5a00;
  font-size: 12px;
}

.api-introduction {
  display: flex;
  flex-direction: column;
  padding: 10px;
  user-select: text;
  background: #f5f5f5;
  border-radius: 8px;

  h4 {
    margin: 15px 0 8px;
    font-size: 16px;
    font-weight: 900;
  }
}

.copy-block {
  position: relative;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #409eff;
    box-shadow: 0 4px 14px rgba(64, 158, 255, 0.12);
  }

  code,
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  }
}

.copy-tip {
  display: inline-block;
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}

.description-block,
.response-block {
  margin: 0;
  padding: 12px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
}

.method-tag {
  display: inline-block;
  min-width: 50px;
  margin-right: 10px;
  font-weight: 700;
}

.method-get {
  color: #409eff;
}

.method-post {
  color: #67c23a;
}

.method-put {
  color: #e6a23c;
}

.method-delete {
  color: #f56c6c;
}

.url-text {
  color: #1f7a8c;
}
</style>
