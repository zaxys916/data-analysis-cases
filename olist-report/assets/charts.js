// assets/charts.js — Olist 项目总结报告
(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var FONT = "'WorkSans', 'Microsoft YaHei', sans-serif";
  function baseAxis() {
    return {
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontFamily: FONT },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: rule } }
    };
  }

  // ---- 图1 RFM 客群 ----
  var c1 = echarts.init(document.getElementById('chart-rfm'), null, { renderer: 'svg' });
  c1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['人数占比%', '金额占比%'], textStyle: { color: ink, fontFamily: FONT } },
    grid: { top: 40, left: 50, right: 30, bottom: 30 },
    xAxis: Object.assign({ type: 'category', data: ['重要发展客户', '重要挽留客户', '重要价值客户', '重要保持客户'] }, baseAxis()),
    yAxis: Object.assign({ type: 'value', name: '%', nameTextStyle: { color: muted } }, baseAxis()),
    series: [
      { name: '人数占比%', type: 'bar', barWidth: 36, data: [59.9, 39.8, 0.17, 0.07],
        itemStyle: { color: accent }, label: { show: true, position: 'top', color: ink, fontFamily: FONT, formatter: '{c}%' } },
      { name: '金额占比%', type: 'bar', barWidth: 36, data: [59.5, 39.7, 0.56, 0.19],
        itemStyle: { color: accent2 }, label: { show: true, position: 'top', color: ink, fontFamily: FONT, formatter: '{c}%' } }
    ]
  });
  window.addEventListener('resize', function() { c1.resize(); });

  // ---- 图2 30天唤醒漏斗 ----
  var c2 = echarts.init(document.getElementById('chart-funnel'), null, { renderer: 'svg' });
  c2.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true, formatter: '{b}: {c} 人' },
    series: [{
      type: 'funnel', sort: 'none', left: '8%', width: '70%', minSize: '3%',
      label: { position: 'inside', color: '#fff', fontFamily: FONT, fontSize: 13,
        formatter: function(p) { return p.name + '  ' + Number(p.value).toLocaleString() + ' 人'; } },
      labelLine: { show: false },
      itemStyle: { borderColor: bg2, borderWidth: 2 },
      data: [
        { name: '首购客户', value: 93358, itemStyle: { color: accent } },
        { name: '30天内累计复购', value: 1417, itemStyle: { color: '#4a89c5' } },
        { name: '90天内累计复购', value: 1875, itemStyle: { color: '#7aa9d6' } },
        { name: '180天内累计复购', value: 2326, itemStyle: { color: '#a8c8e5' } },
        { name: '365天内累计复购', value: 2716, itemStyle: { color: '#c8ddef' } }
      ]
    }],
    graphic: [{
      type: 'text', left: '80%', top: '32%',
      style: { text: '累计留存率\n30天 1.52%\n90天 2.01%\n180天 2.49%\n365天 2.91%\n\n98.5% 在窗口内流失\n每 +1pp ≈ +934 复购客户',
        fill: accent2, fontSize: 13, fontFamily: FONT, lineHeight: 20, textAlign: 'left' }
    }]
  });
  window.addEventListener('resize', function() { c2.resize(); });

  // ---- 图3 月度趋势 ----
  var months = ["2017-01","2017-02","2017-03","2017-04","2017-05","2017-06","2017-07","2017-08","2017-09","2017-10","2017-11","2017-12","2018-01","2018-02","2018-03","2018-04","2018-05","2018-06","2018-07","2018-08"];
  var ordersN = [750,1653,2546,2303,3546,3135,3872,4193,4150,4478,7289,5513,7069,6555,7003,6798,6749,6099,6159,6351];
  var revK = [128,271,414,391,567,490,566,646,701,751,1154,843,1079,967,1121,1133,1129,1012,1028,985];
  var c3 = echarts.init(document.getElementById('chart-trend'), null, { renderer: 'svg' });
  c3.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['订单数', '销售额（千雷亚尔）'], textStyle: { color: ink, fontFamily: FONT } },
    grid: { top: 50, left: 60, right: 70, bottom: 60 },
    xAxis: Object.assign({ type: 'category', data: months, axisLabel: { color: muted, rotate: 45, fontFamily: FONT } }, { axisLine: { lineStyle: { color: rule } }, axisTick: { show: false } }),
    yAxis: [
      Object.assign({ type: 'value', name: '订单数', nameTextStyle: { color: muted } }, baseAxis()),
      Object.assign({ type: 'value', name: '千雷亚尔', nameTextStyle: { color: muted }, splitLine: { show: false } }, baseAxis())
    ],
    series: [
      { name: '订单数', type: 'bar', data: ordersN, itemStyle: { color: accent, opacity: 0.55 } },
      { name: '销售额（千雷亚尔）', type: 'line', yAxisIndex: 1, data: revK, smooth: true,
        lineStyle: { color: accent2, width: 2.5 }, itemStyle: { color: accent2 }, symbolSize: 5,
        markPoint: { data: [{ type: 'max', name: '峰值' }], itemStyle: { color: accent2 }, label: { color: '#fff', fontFamily: FONT } } }
    ]
  });
  window.addEventListener('resize', function() { c3.resize(); });

  // ---- 图4 品类TOP10 ----
  var cats = ['garden_tools', 'auto', 'housewares', 'cool_stuff', 'furniture_decor', 'computers_accessories', 'sports_leisure', 'bed_bath_table', 'watches_gifts', 'health_beauty'];
  var catRev = [485, 593, 632, 635, 730, 912, 988, 1037, 1205, 1259];
  var c4 = echarts.init(document.getElementById('chart-category'), null, { renderer: 'svg' });
  c4.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, formatter: '{b}<br/>销售额: {c} 千雷亚尔' },
    grid: { top: 20, left: 170, right: 50, bottom: 30 },
    xAxis: Object.assign({ type: 'value', name: '千雷亚尔', nameTextStyle: { color: muted } }, baseAxis()),
    yAxis: Object.assign({ type: 'category', data: cats, axisLabel: { color: ink, fontFamily: FONT } }, { axisLine: { lineStyle: { color: rule } }, axisTick: { show: false } }),
    series: [{ type: 'bar', data: catRev, barWidth: 18, itemStyle: { color: accent },
      label: { show: true, position: 'right', color: ink, fontFamily: FONT } }]
  });
  window.addEventListener('resize', function() { c4.resize(); });

  // ---- 图5 价格带 ----
  var c5 = echarts.init(document.getElementById('chart-band'), null, { renderer: 'svg' });
  c5.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['件数占比%', '金额占比%'], textStyle: { color: ink, fontFamily: FONT } },
    grid: { top: 40, left: 50, right: 30, bottom: 30 },
    xAxis: Object.assign({ type: 'category', data: ['<50', '50-100', '100-200', '200-500', '>500'] }, baseAxis()),
    yAxis: Object.assign({ type: 'value', name: '%', nameTextStyle: { color: muted } }, baseAxis()),
    series: [
      { name: '件数占比%', type: 'bar', barWidth: 30, data: [34.9, 29.3, 23.9, 9.0, 2.9],
        itemStyle: { color: accent }, label: { show: true, position: 'top', color: ink, fontFamily: FONT } },
      { name: '金额占比%', type: 'bar', barWidth: 30, data: [9.1, 18.3, 28.5, 22.2, 21.9],
        itemStyle: { color: accent2 }, label: { show: true, position: 'top', color: ink, fontFamily: FONT } }
    ]
  });
  window.addEventListener('resize', function() { c5.resize(); });

  // ---- 图6 支付方式 ----
  var c6 = echarts.init(document.getElementById('chart-pay'), null, { renderer: 'svg' });
  c6.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true, formatter: '{b}<br/>订单占比: {d}%' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: ink, fontFamily: FONT } },
    series: [{
      type: 'pie', radius: ['42%', '68%'], center: ['38%', '50%'],
      label: { color: ink, fontFamily: FONT, formatter: '{b}\n{d}%' },
      data: [
        { name: 'credit_card（信用卡）', value: 75.9, itemStyle: { color: accent } },
        { name: 'boleto（线下缴费）', value: 19.9, itemStyle: { color: accent2 } },
        { name: 'voucher（代金券）', value: 2.7, itemStyle: { color: muted } },
        { name: 'debit_card（借记卡）', value: 1.5, itemStyle: { color: '#9db8d2' } }
      ]
    }],
    graphic: [{
      type: 'text', right: 60, top: '78%',
      style: { text: '51.5% 订单使用分期\n信用卡平均 3.52 期\n信用卡单均 166 vs boleto 144',
        fill: muted, fontSize: 12.5, fontFamily: FONT, lineHeight: 19, textAlign: 'right' }
    }]
  });
  window.addEventListener('resize', function() { c6.resize(); });

  // ---- 图7 评分与差评归因 ----
  var c7 = echarts.init(document.getElementById('chart-score'), null, { renderer: 'svg' });
  c7.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['评分分布（%）', '准时订单差评率', '迟到订单差评率'], textStyle: { color: ink, fontFamily: FONT } },
    grid: { top: 50, left: 50, right: 30, bottom: 30 },
    xAxis: Object.assign({ type: 'category', data: ['1星', '2星', '3星', '4星', '5星'] }, baseAxis()),
    yAxis: Object.assign({ type: 'value', name: '%', nameTextStyle: { color: muted } }, baseAxis()),
    series: [
      { name: '评分分布（%）', type: 'bar', barWidth: 34, data: [9.8, 3.1, 8.3, 19.7, 59.2],
        itemStyle: { color: accent }, label: { show: true, position: 'top', color: ink, fontFamily: FONT } },
      { name: '准时订单差评率', type: 'scatter', symbolSize: 16, data: [[4, 9]], itemStyle: { color: '#2e8b57' },
        label: { show: true, position: 'top', color: ink, fontFamily: FONT, formatter: '准时 9%' } },
      { name: '迟到订单差评率', type: 'scatter', symbolSize: 16, data: [[1, 61]], itemStyle: { color: accent2 },
        label: { show: true, position: 'top', color: ink, fontFamily: FONT, formatter: '迟到 61%' } }
    ]
  });
  window.addEventListener('resize', function() { c7.resize(); });

  // ---- 图8a 同州/跨州运费 ----
  var c8 = echarts.init(document.getElementById('chart-freight'), null, { renderer: 'svg' });
  c8.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, formatter: '{b}<br/>平均运费: {c} 雷亚尔' },
    grid: { top: 20, left: 55, right: 40, bottom: 30 },
    xAxis: Object.assign({ type: 'category', data: ['同州配送', '跨州配送'] }, baseAxis()),
    yAxis: Object.assign({ type: 'value', name: '雷亚尔', nameTextStyle: { color: muted } }, baseAxis()),
    series: [{ type: 'bar', barWidth: 44, data: [
      { value: 13.45, itemStyle: { color: accent } },
      { value: 23.63, itemStyle: { color: accent2 } }
    ], label: { show: true, position: 'top', color: ink, fontFamily: FONT } }]
  });
  window.addEventListener('resize', function() { c8.resize(); });

  // ---- 图8b 州运费对比 ----
  var c9 = echarts.init(document.getElementById('chart-state'), null, { renderer: 'svg' });
  c9.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true, formatter: '{b}<br/>平均运费: {c} 雷亚尔' },
    grid: { top: 20, left: 55, right: 60, bottom: 30 },
    xAxis: Object.assign({ type: 'value', name: '雷亚尔', nameTextStyle: { color: muted } }, baseAxis()),
    yAxis: Object.assign({ type: 'category',
      data: ['SP', 'PR', 'MG', 'RJ', 'DF', 'PA', 'RN', 'MA', 'PI', 'PB'],
      axisLabel: { color: ink, fontFamily: FONT } },
      { axisLine: { lineStyle: { color: rule } }, axisTick: { show: false } }),
    series: [{ type: 'bar', barWidth: 14, data: [
      { value: 15.12, itemStyle: { color: accent } },
      { value: 20.47, itemStyle: { color: accent } },
      { value: 20.63, itemStyle: { color: accent } },
      { value: 20.91, itemStyle: { color: accent } },
      { value: 21.07, itemStyle: { color: accent } },
      { value: 35.63, itemStyle: { color: accent2 } },
      { value: 35.72, itemStyle: { color: accent2 } },
      { value: 38.49, itemStyle: { color: accent2 } },
      { value: 39.12, itemStyle: { color: accent2 } },
      { value: 43.09, itemStyle: { color: accent2 } }
    ], label: { show: true, position: 'right', color: ink, fontFamily: FONT } }]
  });
  window.addEventListener('resize', function() { c9.resize(); });
})();
