// -*- coding: utf-8 -*-
/**
 * P3dPyPad Web - 双语国际化 (i18n) 语言引擎 (中文 / English)
 * 支持用户手动切换与 LocalStorage 本地持久化记忆，默认按系统区域探测首选语言
 */

export const LANG_ZH = 'zh';
export const LANG_EN = 'en';

const STORAGE_KEY = 'p3dpypad_lang_pref';

let currentLang = LANG_ZH;
const listeners = [];

export const DICTIONARY = {
  // 顶部标题栏
  app_title: {
    zh: 'Plant 3D PyOCC 仿真工作台',
    en: 'Plant 3D PyOCC Simulation Studio'
  },
  chip_wasm: {
    zh: 'OpenCASCADE 8.0.1 WASM',
    en: 'OpenCASCADE 8.0.1 WASM'
  },
  lang_zh: { zh: '中文', en: '中文' },
  lang_en: { zh: 'English', en: 'English' },

  // 左侧操作区
  search_placeholder: {
    zh: '搜索构件 (如 弯头 / 阀门 / CD)...',
    en: 'Search components (e.g. Elbow / Valve / CD)...'
  },
  search_title: {
    zh: '输入构件位号或中文关键字即时过滤',
    en: 'Filter by component ID or keyword'
  },
  btn_run: {
    zh: '运行 (F5)',
    en: 'Run (F5)'
  },
  btn_run_tip: {
    zh: '执行脚本建模 (快捷键 F5 或 Ctrl+Enter)',
    en: 'Execute modeling script (F5 or Ctrl+Enter)'
  },
  btn_reset: {
    zh: '重置',
    en: 'Reset'
  },
  btn_reset_tip: {
    zh: '重置代码为当前构件初始源码',
    en: 'Reset code to initial script source'
  },
  select_preset_title: {
    zh: '选择 pyscripts 构件脚本',
    en: 'Select component from pyscripts'
  },
  select_no_match: {
    zh: '未找到匹配构件',
    en: 'No matching components'
  },
  section_code: {
    zh: 'Python 源码',
    en: 'Python Source Code'
  },
  code_placeholder: {
    zh: '在此粘贴 AutoCAD Plant 3D 构件 Python 脚本代码...',
    en: 'Paste AutoCAD Plant 3D Python component script here...'
  },
  section_params: {
    zh: '尺寸参数',
    en: 'Dimensional Parameters'
  },
  params_empty: {
    zh: '该构件无需额外调节参数',
    en: 'No adjustable parameters for this component'
  },

  // 视口工具栏
  view_iso: { zh: '轴测', en: 'Iso' },
  view_iso_tip: { zh: '正交等轴测视角', en: 'Orthographic Isometric View' },
  view_top: { zh: '俯视', en: 'Top' },
  view_top_tip: { zh: '正交俯视图 (XY 平面)', en: 'Top View (XY Plane)' },
  view_front: { zh: '正视', en: 'Front' },
  view_front_tip: { zh: '正交正视图 (XZ 平面)', en: 'Front View (XZ Plane)' },
  view_side: { zh: '侧视', en: 'Side' },
  view_side_tip: { zh: '正交侧视图 (YZ 平面)', en: 'Side View (YZ Plane)' },
  view_fit: { zh: '居中', en: 'Fit' },
  view_fit_tip: { zh: '视口自适应居中缩放', en: 'Fit View to Model' },

  // 渲染模式
  render_shaded_edges: { zh: '着色边线', en: 'Shaded with Edges' },
  render_shaded: { zh: '实体着色', en: 'Shaded Only' },
  render_wireframe: { zh: '线框模式', en: 'Wireframe' },
  render_mode_tip: { zh: '切换渲染模式', en: 'Switch Render Mode' },

  // 材质颜色
  color_blue: { zh: '工程蓝', en: 'Engineering Blue' },
  color_gray: { zh: '工业灰', en: 'Industrial Gray' },
  color_teal: { zh: '钢青色', en: 'Steel Cyan' },
  color_orange: { zh: '机械橙', en: 'Safety Orange' },
  color_green: { zh: '设备绿', en: 'Equipment Green' },
  color_select_tip: { zh: '构件材质颜色', en: 'Component Material Color' },

  // 预览按钮
  btn_snapshot: { zh: '生成预览图', en: 'Generate Snapshot' },
  btn_snapshot_tip: {
    zh: '一键生成高精度双模轴测预览图 (标准+标注 PNG)',
    en: 'Generate high-res dual isometric snapshots (Clean + Annotated PNG)'
  },

  // 加载提示
  loading_wasm: {
    zh: '正在加载 OpenCASCADE 几何造型内核 (WASM)...',
    en: 'Loading OpenCASCADE Geometry Kernel (WASM)...'
  },
  loading_kernel_ok: {
    zh: 'OpenCASCADE 几何造型内核就绪！',
    en: 'OpenCASCADE Geometry Kernel Ready!'
  },
  loading_modeling: {
    zh: '正在进行 OpenCASCADE 实体造型...',
    en: 'Modeling OpenCASCADE B-Rep Solids...'
  },
  loading_meshing: {
    zh: '正在离散剖分 B-Rep 实体与边界特征线...',
    en: 'Tessellating B-Rep Solids and Feature Edges...'
  },
  loading_snapshot: {
    zh: '正在生成标准轴测与尺寸标注两套高清出图...',
    en: 'Rendering Clean & Annotated Isometric Snapshots...'
  },
  loading_default: {
    zh: '正在处理中...',
    en: 'Processing...'
  },

  // 运行日志与状态
  log_title: { zh: '运行日志', en: 'Execution Logs' },
  badge_ready: { zh: '就绪', en: 'Ready' },
  badge_running: { zh: '运行中', en: 'Running' },
  badge_success: { zh: '成功', en: 'Success' },
  badge_error: { zh: '错误', en: 'Error' },
  btn_clear_log: { zh: '清空日志', en: 'Clear Logs' },
  btn_clear_log_tip: { zh: '清空全部日志', en: 'Clear All Log Entries' },
  btn_toggle_collapse: { zh: '收起', en: 'Collapse' },
  btn_toggle_expand: { zh: '展开', en: 'Expand' },
  btn_toggle_tip: { zh: '折叠或展开日志面板', en: 'Toggle Log Panel' },
  status_ready: { zh: '准备就绪', en: 'Ready' },
  status_log_cleared: { zh: '日志已清空', en: 'Logs cleared' },
  status_reading_script: {
    zh: '正在读取构件脚本: {name}...',
    en: 'Loading component script: {name}...'
  },
  status_catalog_loaded: {
    zh: '已加载 pyscripts 构件库资产 ({count} 个构件)',
    en: 'Loaded pyscripts component library ({count} components)'
  },
  status_model_completed: {
    zh: '构件 {name} 建模完成: 耗时 {time} ms | 面数 {faces} | 三角面 {triangles} | 包络 {bbox} | 端口 {ports} | 尺寸标注 {dims}',
    en: 'Component {name} modeling completed: Time {time} ms | Faces {faces} | Triangles {triangles} | Bounding Box {bbox} | Ports {ports} | Dimensions {dims}'
  },
  status_model_error: {
    zh: '执行错误: {msg}',
    en: 'Execution error: {msg}'
  },

  // 出图预览对话框
  dialog_title: { zh: '三维出图预览', en: '3D Snapshot Preview' },
  tab_clean: { zh: '标准轴测图', en: 'Standard Isometric' },
  tab_clean_tip: { zh: '纯实体着色轴测出图 (无标注)', en: 'Clean shaded isometric snapshot (No dimensions)' },
  tab_annotated: { zh: '轴测尺寸图', en: 'Annotated Isometric' },
  tab_annotated_tip: { zh: '带工程尺寸标注的轴测图', en: 'Isometric snapshot with engineering dimensions' },
  btn_close: { zh: '关闭', en: 'Close' },
  btn_download_current: { zh: '下载当前图', en: 'Download Current' },
  btn_download_all: { zh: '下载两张 (标准+标注)', en: 'Download Both (Clean + Annotated)' },
  snapshot_meta_clean: {
    zh: '构件: {name} (标准轴测出图) | 分辨率: {w} × {h} px | 格式: PNG',
    en: 'Component: {name} (Standard Isometric) | Resolution: {w} × {h} px | Format: PNG'
  },
  snapshot_meta_annotated: {
    zh: '构件: {name} (带工程尺寸标注) | 分辨率: {w} × {h} px | 格式: PNG',
    en: 'Component: {name} (With Engineering Dimensions) | Resolution: {w} × {h} px | Format: PNG'
  },
  alert_no_model: {
    zh: '当前尚未生成有效的 3D 模型，请先运行建模！',
    en: 'No valid 3D model generated yet. Please run modeling first!'
  }
};

/**
 * 分类名称双语对照表
 */
export const CATEGORY_NAMES_EN = {
  '01 管道管件 (Pipe Fittings)': '01 Pipe Fittings',
  '02 法兰垫片 (Flanges & Gaskets)': '02 Flanges & Gaskets',
  '03 阀门类 (Valves)': '03 Valves & Actuators',
  '04 仪器仪表 (Instruments)': '04 Instruments',
  '05 支吊架 (Supports & Hangers)': '05 Supports & Hangers',
  '06 工艺设备与泵 (Equipment & Pumps)': '06 Equipment & Pumps',
  '07 系统内置原厂构件 (System Defaults)': '07 System Defaults',
  '通用构件': 'General Components'
};

/**
 * 初始化并检测首选语言 (优先 LocalStorage，次选系统浏览器区域)
 */
export function initLanguage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === LANG_ZH || saved === LANG_EN) {
      currentLang = saved;
      return currentLang;
    }
  } catch (e) {
    // 忽略 localStorage 异常
  }

  const navLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
  currentLang = navLang.startsWith('zh') ? LANG_ZH : LANG_EN;
  return currentLang;
}

/**
 * 获取当前语言
 */
export function getLanguage() {
  return currentLang;
}

/**
 * 切换并持久化当前语言
 */
export function setLanguage(lang) {
  if (lang !== LANG_ZH && lang !== LANG_EN) return;
  currentLang = lang;
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch (e) {
    // 忽略 localStorage 异常
  }
  for (const fn of listeners) {
    try {
      fn(currentLang);
    } catch (e) {
      console.warn('i18n listener error:', e);
    }
  }
}

/**
 * 注册语言切换事件监听器
 */
export function onLanguageChange(fn) {
  if (typeof fn === 'function' && !listeners.includes(fn)) {
    listeners.push(fn);
  }
}

/**
 * 翻译文本并替换占位符 {key}
 */
export function t(key, params = {}) {
  const item = DICTIONARY[key];
  if (!item) return key;
  let text = item[currentLang] || item[LANG_ZH] || key;
  if (params && typeof params === 'object') {
    for (const [k, v] of Object.entries(params)) {
      text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
    }
  }
  return text;
}
