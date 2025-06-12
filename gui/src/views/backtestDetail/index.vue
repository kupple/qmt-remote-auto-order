<template>
  <div class="backtest-container">
    <div class="backtest-header">
      <div class="backtest-header-item">股票名称</div>
      <div class="backtest-header-item">数量</div>
      <div class="backtest-header-item">方向</div>
      <div class="backtest-header-item">持仓均价</div>
      <div class="backtest-header-item">手续费</div>
      <div class="backtest-header-item">市值</div>
    </div>
    <div class="backtest-content">
      <div v-for="item in tableData" :key="item.id" class="backtest-content-item">
        <div class="backtest-content-item-date">
          {{ item.date }}
        </div>
        <div class="section">
          <span>持仓</span>
        </div>
        <div v-for="(stock, idx) in item.positions" class="backtest-content-item-stocks" :key="idx">
          <div class="backtest-content-item-stocks-item">{{ stock.stock_code }}</div>
          <div class="backtest-content-item-stocks-item">{{ stock.volume }}</div>
          <div class="backtest-content-item-stocks-item"></div>
          <div class="backtest-content-item-stocks-item">{{ stock.avg_price }}</div>
          <div class="backtest-content-item-stocks-item"></div>
          <div class="backtest-content-item-stocks-item">{{(stock.volume * stock.avg_price).toFixed(2)}}</div>
        </div>
        <!-- 现金 -->
        <div class="backtest-content-item-stocks">
          <div class="backtest-content-item-stocks-item">
            <el-tag disable-transitions	 size="small">现金</el-tag>
          </div>
          <div class="backtest-content-item-stocks-item"></div>
          <div class="backtest-content-item-stocks-item"></div>
          <div class="backtest-content-item-stocks-item"></div>
          <div class="backtest-content-item-stocks-item"></div>
          <div class="backtest-content-item-stocks-item">{{item.remaining_cash.toFixed(2)}}</div>
        </div>
        <div class="section" v-if="item.trades.length > 0">
          <span>当日变动</span>
        </div>
        <div v-for="(stock, idx) in item.trades" class="backtest-content-item-trades" :key="idx">
          <div class="backtest-content-item-trades-item">{{ stock.stock_code }}</div>
          <div class="backtest-content-item-trades-item">{{ stock.volume }}</div>
          <div class="backtest-content-item-trades-item">
            <el-tag disable-transitions	 size="small" type="success" v-if="stock.direction == '买入'">买入</el-tag>
            <el-tag disable-transitions	 size="small" type="danger" v-else>卖出</el-tag></div>
          <div class="backtest-content-item-trades-item"></div>
          <div class="backtest-content-item-trades-item"></div>
          <div class="backtest-content-item-trades-item">
            <span v-if="stock.direction == '买入'">+</span>
            <span v-else>-</span>
            {{ (stock.price * stock.volume).toFixed(2) }}
          </div>
        </div>
        <div class="backtest-content-item-footer">
          <div class="backtest-content-item-footer-item"></div>
          <div class="backtest-content-item-footer-item"></div>
          <div class="backtest-content-item-footer-item"></div>
          <div class="backtest-content-item-footer-item"></div>
          <div class="backtest-content-item-footer-item"></div>
          <div class="backtest-content-item-footer-item">共:{{ item.total_profit.toFixed(2) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { countStrategyAnalyzer } from '@/api/comm_tube'
const route = useRoute()
const tableData = ref([])

const getBacktestList = async () => {
  const backtest_id = route.query.id
  const res = await countStrategyAnalyzer(null, backtest_id)
  console.log(res)
  tableData.value = res.daily_positions
}

onMounted(() => {
  getBacktestList()
})
</script>

<style scoped lang="less">
.backtest-container {
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
  height: 100%;
  display: flex;
  flex-direction: column;
  .backtest-header {
    display: flex;
    justify-content: space-between;
    background: var(--el-text-color-primary);
    color: #fff;

    height: 30px;
    .backtest-header-item {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 14px;
    }
  }
  .backtest-content {
    flex: 1;
    background: #fff;
    width: 100%;
    overflow: auto;
    // padding-left:10px;
    .section {
      padding-left: 15px;
      font-weight: bold;
      height: 30px;
      display: flex;
      width: 100%;
      align-items: center;
      background: var(--el-color-info-light-9);
      box-sizing: border-box;
      font-size: 14px;
    }
    .backtest-content-item {
      .backtest-content-item-date {
        height: 30px;
        background: var(--el-border-color);
        display: flex;
        // justify-content: center;
        align-items: center;
        padding-left: 10px;
        font-weight: bold;
      }
      .backtest-content-item-stocks {
        display: flex;
        // flex-direction: column;

        // flex-direction:column;
        .backtest-content-item-stocks-item {
          flex: 1;
          display: flex;
          justify-content: center;
          align-items: center;
          border-top: 1px solid #f2f2f2;
          border-bottom: 1px solid #f2f2f2;
          height: 30px;
          font-size: 14px;
        }
        .backtest-content-item-stocks-footer {
          display: flex;
          .backtest-content-item-stocks-footer-item {
            height: 30px;
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
          }
        }
      }
      .backtest-content-item-footer {
        height: 30px;
        display: flex;
        align-items: center;
        font-size: 16px;
        background: var(--el-color-info-light-3);

        .backtest-content-item-footer-item {
          flex: 1;
          display: flex;
          justify-content: center;
          align-items: center;
          font-size: 14px;
        }
      }
      .backtest-content-item-trades {
        display: flex;
        height: 30px;
        .backtest-content-item-trades-item {
          flex: 1;
          display: flex;
          justify-content: center;
          align-items: center;
          border-top: 1px solid #f2f2f2;
          border-bottom: 1px solid #f2f2f2;
          font-size: 14px;
        }
      }
    }
  }
}
</style>
