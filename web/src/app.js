// -*- coding: utf-8 -*-
/**
 * P3dPyPad Web - 主应用程序控制器 (UI 交互、Three.js 视口管理与构件三维预览)
 * 采用极简 Material Design 风格，纯文本交互，无任何图标修饰，原生支持中英双语 (i18n)
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import * as kernel from './kernel.js';
import { extractScriptMetadata, runPlant3dScript } from './transpiler.js';
import { PRESET_SCRIPTS } from './presets.js';
import { create3dDimensionsObject } from './dimensions.js';
import {
  LANG_ZH,
  LANG_EN,
  initLanguage,
  getLanguage,
  setLanguage,
  onLanguageChange,
  t,
  CATEGORY_NAMES_EN
} from './i18n.js';

// 全局状态管理
let scene, camera, renderer, controls;
let modelGroup = null;
let currentShape = null;
let currentMesh = null;
let currentEdges = null;
let currentSession = null;
let currentMetadata = null;
let currentParams = {};
let currentFramingPoints = [];
let currentSnapshots = { clean: '', annotated: '', activeTab: 'clean', compName: '' };
let isRendering = false;
let renderMode = 'shaded_edges'; // 'shaded_edges' | 'shaded' | 'wireframe'
let modelColor = '#388bfd';
let allScriptCatalog = []; // 存储 pyscripts 全库构件索引
let currentScriptItem = null;

const els = {};

/**
 * 显示/隐藏视口加载遮罩
 */
function showLoading(text) {
  if (els.loadingText) els.loadingText.textContent = text || t('loading_default');
  if (els.viewportLoading) els.viewportLoading.classList.remove('hidden');
  if (els.btnRun) {
    els.btnRun.classList.add('loading');
    els.btnRun.disabled = true;
  }
}

function hideLoading() {
  if (els.viewportLoading) els.viewportLoading.classList.add('hidden');
  if (els.btnRun) {
    els.btnRun.classList.remove('loading');
    els.btnRun.disabled = false;
  }
}

/**
 * 页面加载完成初始化入口
 */
window.addEventListener('DOMContentLoaded', async () => {
  cacheDOMElements();
  initLanguage();
  initThreeViewport();
  bindUIEvents();
  applyLanguage(getLanguage());

  try {
    showLoading(t('loading_wasm'));
    updateStatus(t('loading_wasm'), 'info');
    await kernel.initOpenCascade(msg => {
      updateStatus(msg, 'info');
      if (els.loadingText) els.loadingText.textContent = msg;
    });
    updateStatus(t('loading_kernel_ok'), 'success');

    // 加载 pyscripts 构件库清单
    await initScriptCatalog();

    // 默认加载首个构件并建模
    await loadInitialScript();
  } catch (err) {
    console.error('内核初始化失败:', err);
    updateStatus(`内核加载失败: ${err.message}`, 'error');
  } finally {
    hideLoading();
  }
});

/**
 * 缓存常用 DOM 元素
 */
function cacheDOMElements() {
  els.brandTitle = document.getElementById('brand-title');
  els.btnLangZh = document.getElementById('btn-lang-zh');
  els.btnLangEn = document.getElementById('btn-lang-en');
  els.lblCode = document.getElementById('lbl-code');
  els.lblParams = document.getElementById('lbl-params');
  els.lblLogTitle = document.getElementById('lbl-log-title');
  els.dialogTitle = document.getElementById('dialog-title');

  els.viewportContainer = document.getElementById('viewport-container');
  els.viewportLoading = document.getElementById('viewport-loading');
  els.loadingText = document.getElementById('loading-text');
  els.codeEditor = document.getElementById('code-editor');
  els.scriptSearch = document.getElementById('script-search');
  els.presetSelect = document.getElementById('preset-select');
  els.btnRun = document.getElementById('btn-run');
  els.btnReset = document.getElementById('btn-reset');
  els.btnSnapshot = document.getElementById('btn-snapshot');
  els.btnFit = document.getElementById('btn-fit');
  els.btnIso = document.getElementById('btn-iso');
  els.btnTop = document.getElementById('btn-top');
  els.btnFront = document.getElementById('btn-front');
  els.btnSide = document.getElementById('btn-side');
  els.renderModeSelect = document.getElementById('render-mode-select');
  els.colorSelect = document.getElementById('color-select');
  els.paramContainer = document.getElementById('param-container');
  els.statusQuick = document.getElementById('status-quick');
  els.logPanel = document.getElementById('log-panel');
  els.logList = document.getElementById('log-list');
  els.logStatusBadge = document.getElementById('log-status-badge');
  els.btnClearLog = document.getElementById('btn-clear-log');
  els.btnToggleLog = document.getElementById('btn-toggle-log');
  els.snapshotModal = document.getElementById('snapshot-modal');
  els.snapshotImg = document.getElementById('snapshot-img');
  els.snapshotInfo = document.getElementById('snapshot-info');
  els.tabPreviewClean = document.getElementById('tab-preview-clean');
  els.tabPreviewAnnotated = document.getElementById('tab-preview-annotated');
  els.btnDownloadSnapshot = document.getElementById('btn-download-snapshot');
  els.btnDownloadAll = document.getElementById('btn-download-all');
  els.btnCloseModal = document.getElementById('btn-close-modal');
  els.btnDialogClose = document.getElementById('btn-dialog-close');
}

/**
 * 异步加载 pyscripts 全库构件资产清单
 */
async function initScriptCatalog() {
  try {
    const resp = await fetch('./public/pyscripts_manifest.json');
    if (resp.ok) {
      allScriptCatalog = await resp.json();
      updateStatus(t('status_catalog_loaded', { count: allScriptCatalog.length }), 'info');
    } else {
      throw new Error(`HTTP ${resp.status}`);
    }
  } catch (e) {
    console.warn('获取 pyscripts_manifest 失败，使用内置经典构件预设:', e);
    allScriptCatalog = PRESET_SCRIPTS.map(p => ({
      id: p.id,
      name: p.id,
      title: p.name,
      category: p.category,
      code: p.code,
      description: p.description
    }));
  }

  renderScriptDropdown();
}

/**
 * 渲染构件下拉菜单 (按分类 optgroup 分组，支持关键字过滤与中英双语标签)
 */
function renderScriptDropdown(filterText = '') {
  const query = filterText.trim().toLowerCase();
  els.presetSelect.innerHTML = '';
  const isEn = getLanguage() === LANG_EN;

  const filtered = allScriptCatalog.filter(item => {
    if (!query) return true;
    return (
      item.name.toLowerCase().includes(query) ||
      (item.title && item.title.toLowerCase().includes(query)) ||
      (item.category && item.category.toLowerCase().includes(query)) ||
      (item.description && item.description.toLowerCase().includes(query))
    );
  });

  if (filtered.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = t('select_no_match');
    els.presetSelect.appendChild(opt);
    return;
  }

  // 按类别分组
  const groups = {};
  for (let item of filtered) {
    let cat = item.category || '通用构件';
    if (isEn && CATEGORY_NAMES_EN[cat]) {
      cat = CATEGORY_NAMES_EN[cat];
    }
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(item);
  }

  for (let cat of Object.keys(groups)) {
    const grp = document.createElement('optgroup');
    grp.label = `${cat} (${groups[cat].length})`;
    for (let item of groups[cat]) {
      const opt = document.createElement('option');
      opt.value = item.id;
      if (isEn) {
        opt.textContent = item.name + (item.title && item.title !== item.name ? ` (${item.name})` : '');
      } else {
        opt.textContent = item.title || item.name;
      }
      grp.appendChild(opt);
    }
    els.presetSelect.appendChild(grp);
  }

  // 保持当前选中的构件处于选中状态
  if (currentScriptItem && filtered.some(i => i.id === currentScriptItem.id)) {
    els.presetSelect.value = currentScriptItem.id;
  } else if (filtered.length > 0) {
    els.presetSelect.value = filtered[0].id;
  }
}

/**
 * 加载初始构件 (默认加载经典 90度长半径无缝对焊弯头)
 */
async function loadInitialScript() {
  const defaultItem = allScriptCatalog.find(i => i.name === 'ELBOW_90' || i.id === 'ELBOW_90') || allScriptCatalog[0];
  if (defaultItem) {
    els.presetSelect.value = defaultItem.id;
    await loadScriptById(defaultItem.id);
  }
}

/**
 * 根据 ID 加载指定构件脚本代码并执行建模
 */
async function loadScriptById(scriptId) {
  const item = allScriptCatalog.find(i => i.id === scriptId || i.name === scriptId) || allScriptCatalog[0];
  if (!item) return;

  currentScriptItem = item;
  currentParams = {}; // 重置参数表

  try {
    if (item.code) {
      els.codeEditor.value = item.code.trim();
    } else if (item.path) {
      updateStatus(t('status_reading_script', { name: item.name }), 'info');
      const fetchPath = item.path.startsWith('./') ? item.path : `./${item.path}`;
      const resp = await fetch(fetchPath);
      if (!resp.ok) throw new Error(`加载脚本失败: HTTP ${resp.status}`);
      const code = await resp.text();
      els.codeEditor.value = code.trim();
    }
    refreshParameterPanel();
    await executeCurrentCode();
  } catch (err) {
    console.error('加载构件脚本失败:', err);
    updateStatus(t('status_model_error', { msg: err.message }), 'error');
  }
}

/**
 * 初始化 Three.js 三维视口 (正交工程投影 Orthographic + 无惯性阻尼 No Damping + 无网格 No Grid)
 */
function initThreeViewport() {
  const width = els.viewportContainer.clientWidth || 800;
  const height = els.viewportContainer.clientHeight || 600;
  const aspect = width / height;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf8fafc); // CAD 纯净浅色工程背景底色 (Slate-50)

  // 正交相机 (OrthographicCamera)：保证真实工程 1:1 投影，平行线绝不汇聚，消除透视畸变
  const frustumSize = 400;
  camera = new THREE.OrthographicCamera(
    -frustumSize * aspect / 2,
    frustumSize * aspect / 2,
    frustumSize / 2,
    -frustumSize / 2,
    -50000,
    50000
  );
  camera.up.set(0, 0, 1); // CAD Z 轴朝上
  camera.position.set(400, -400, 400);

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    preserveDrawingBuffer: true,
    powerPreference: 'high-performance'
  });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;

  els.viewportContainer.appendChild(renderer.domElement);

  // OrbitControls: 禁用惯性阻尼 (enableDamping = false)，停手即止，精准 CAD 工业手感
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = false;
  controls.screenSpacePanning = true;
  controls.target.set(0, 0, 0);
  controls.update();

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);

  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x94a3b8, 0.6);
  scene.add(hemiLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 0.85);
  mainLight.position.set(300, -200, 400);
  scene.add(mainLight);

  const fillLight = new THREE.DirectionalLight(0xe2e8f0, 0.5);
  fillLight.position.set(-300, 200, 200);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0xffffff, 0.4);
  rimLight.position.set(0, 0, -300);
  scene.add(rimLight);

  // 无网格 (No Grid)：严格遵循用户需求，不添加任何背景网格

  const axesHelper = new THREE.AxesHelper(80);
  axesHelper.name = 'CAD_AXES';
  scene.add(axesHelper);

  modelGroup = new THREE.Group();
  scene.add(modelGroup);

  window.addEventListener('resize', onWindowResize);
  animate();
}

function onWindowResize() {
  if (!els.viewportContainer) return;
  const width = els.viewportContainer.clientWidth;
  const height = els.viewportContainer.clientHeight;
  if (width === 0 || height === 0) return;

  const aspect = width / height;
  const currentHeight = camera.top - camera.bottom;
  camera.left = -currentHeight * aspect / 2;
  camera.right = currentHeight * aspect / 2;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

/**
 * 绑定界面各类操作按钮与交互事件 (纯文本，无图标)
 */
function bindUIEvents() {
  els.presetSelect.addEventListener('change', () => {
    if (els.presetSelect.value) {
      loadScriptById(els.presetSelect.value);
    }
  });

  els.btnRun.addEventListener('click', () => {
    executeCurrentCode();
  });

  els.btnReset.addEventListener('click', () => {
    if (currentScriptItem) {
      loadScriptById(currentScriptItem.id);
    } else if (els.presetSelect.value) {
      loadScriptById(els.presetSelect.value);
    }
  });

  if (els.scriptSearch) {
    let searchTimer = null;
    els.scriptSearch.addEventListener('input', e => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        renderScriptDropdown(e.target.value);
      }, 200);
    });

    els.scriptSearch.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (els.presetSelect.value) {
          loadScriptById(els.presetSelect.value);
        }
      }
    });
  }

  window.addEventListener('keydown', e => {
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'Enter')) {
      e.preventDefault();
      executeCurrentCode();
    }
  });

  let codeChangeTimer = null;
  els.codeEditor.addEventListener('input', () => {
    clearTimeout(codeChangeTimer);
    codeChangeTimer = setTimeout(() => {
      refreshParameterPanel();
    }, 400);
  });

  if (els.btnFit) {
    els.btnFit.addEventListener('click', () => fitViewToModel());
  }

  const viewBtns = [
    { btn: els.btnIso, preset: 'iso' },
    { btn: els.btnTop, preset: 'top' },
    { btn: els.btnFront, preset: 'front' },
    { btn: els.btnSide, preset: 'side' }
  ];

  viewBtns.forEach(({ btn, preset }) => {
    if (!btn) return;
    btn.addEventListener('click', () => {
      viewBtns.forEach(v => v.btn?.classList.remove('active'));
      btn.classList.add('active');
      setViewPreset(preset);
    });
  });

  // 当用户在画布上手动旋转视口时，如果偏离了预设正交方向，自动清除分段按钮选中态
  if (controls) {
    controls.addEventListener('start', () => {
      viewBtns.forEach(v => v.btn?.classList.remove('active'));
    });
  }

  els.renderModeSelect.addEventListener('change', () => {
    renderMode = els.renderModeSelect.value;
    updateModelRenderMode();
  });

  els.colorSelect.addEventListener('change', () => {
    modelColor = els.colorSelect.value;
    if (currentMesh && currentMesh.material) {
      currentMesh.material.color.set(modelColor);
    }
  });

  if (els.btnGridToggle) {
    els.btnGridToggle.addEventListener('click', () => {
      const grid = scene.getObjectByName('CAD_GRID');
      if (grid) grid.visible = !grid.visible;
    });
  }

  els.btnSnapshot.addEventListener('click', () => {
    generatePreviewSnapshot();
  });

  if (els.btnClearLog) {
    els.btnClearLog.addEventListener('click', () => {
      if (els.logList) els.logList.innerHTML = '';
      updateStatus(t('status_log_cleared'), 'info');
    });
  }

  if (els.btnToggleLog) {
    els.btnToggleLog.addEventListener('click', () => {
      if (els.logPanel) {
        const isCollapsed = els.logPanel.classList.toggle('collapsed');
        els.btnToggleLog.textContent = isCollapsed ? t('btn_toggle_expand') : t('btn_toggle_collapse');
        setTimeout(() => {
          onWindowResize();
        }, 160);
      }
    });
  }

  if (els.btnLangZh) {
    els.btnLangZh.addEventListener('click', () => setLanguage(LANG_ZH));
  }
  if (els.btnLangEn) {
    els.btnLangEn.addEventListener('click', () => setLanguage(LANG_EN));
  }
  onLanguageChange(lang => {
    applyLanguage(lang);
  });

  if (els.tabPreviewClean) {
    els.tabPreviewClean.addEventListener('click', () => switchPreviewTab('clean'));
  }
  if (els.tabPreviewAnnotated) {
    els.tabPreviewAnnotated.addEventListener('click', () => switchPreviewTab('annotated'));
  }

  const closeModal = () => els.snapshotModal.classList.add('hidden');
  els.btnCloseModal.addEventListener('click', closeModal);
  if (els.btnDialogClose) els.btnDialogClose.addEventListener('click', closeModal);

  els.snapshotModal.addEventListener('click', e => {
    if (e.target === els.snapshotModal) {
      closeModal();
    }
  });
}

/**
 * 应用双语本地化翻译至全站界面元素
 */
function applyLanguage(lang) {
  // 切换语言按钮高亮
  if (lang === LANG_ZH) {
    els.btnLangZh?.classList.add('active');
    els.btnLangEn?.classList.remove('active');
  } else {
    els.btnLangZh?.classList.remove('active');
    els.btnLangEn?.classList.add('active');
  }

  // 顶部标题
  if (els.brandTitle) els.brandTitle.textContent = t('app_title');

  // 左侧操作面板
  if (els.scriptSearch) {
    els.scriptSearch.placeholder = t('search_placeholder');
    els.scriptSearch.title = t('search_title');
  }
  if (els.btnRun) {
    els.btnRun.textContent = t('btn_run');
    els.btnRun.title = t('btn_run_tip');
  }
  if (els.btnReset) {
    els.btnReset.textContent = t('btn_reset');
    els.btnReset.title = t('btn_reset_tip');
  }
  if (els.presetSelect) {
    els.presetSelect.title = t('select_preset_title');
  }
  if (els.lblCode) els.lblCode.textContent = t('section_code');
  if (els.codeEditor) els.codeEditor.placeholder = t('code_placeholder');
  if (els.lblParams) els.lblParams.textContent = t('section_params');

  // 视口工具栏分段按钮
  if (els.btnIso) { els.btnIso.textContent = t('view_iso'); els.btnIso.title = t('view_iso_tip'); }
  if (els.btnTop) { els.btnTop.textContent = t('view_top'); els.btnTop.title = t('view_top_tip'); }
  if (els.btnFront) { els.btnFront.textContent = t('view_front'); els.btnFront.title = t('view_front_tip'); }
  if (els.btnSide) { els.btnSide.textContent = t('view_side'); els.btnSide.title = t('view_side_tip'); }
  if (els.btnFit) { els.btnFit.textContent = t('view_fit'); els.btnFit.title = t('view_fit_tip'); }

  // 渲染模式下拉
  if (els.renderModeSelect) {
    els.renderModeSelect.title = t('render_mode_tip');
    const opts = els.renderModeSelect.options;
    if (opts.length >= 3) {
      opts[0].textContent = t('render_shaded_edges');
      opts[1].textContent = t('render_shaded');
      opts[2].textContent = t('render_wireframe');
    }
  }

  // 颜色下拉
  if (els.colorSelect) {
    els.colorSelect.title = t('color_select_tip');
    const opts = els.colorSelect.options;
    if (opts.length >= 5) {
      opts[0].textContent = t('color_blue');
      opts[1].textContent = t('color_gray');
      opts[2].textContent = t('color_teal');
      opts[3].textContent = t('color_orange');
      opts[4].textContent = t('color_green');
    }
  }

  // 生成预览图按钮
  if (els.btnSnapshot) {
    els.btnSnapshot.textContent = t('btn_snapshot');
    els.btnSnapshot.title = t('btn_snapshot_tip');
  }

  // 日志面板与状态
  if (els.lblLogTitle) els.lblLogTitle.textContent = t('log_title');
  if (els.btnClearLog) {
    els.btnClearLog.textContent = t('btn_clear_log');
    els.btnClearLog.title = t('btn_clear_log_tip');
  }
  if (els.btnToggleLog) {
    const isCollapsed = els.logPanel?.classList.contains('collapsed');
    els.btnToggleLog.textContent = isCollapsed ? t('btn_toggle_expand') : t('btn_toggle_collapse');
    els.btnToggleLog.title = t('btn_toggle_tip');
  }
  if (els.logStatusBadge) {
    els.logStatusBadge.textContent = t('badge_ready');
  }

  // 出图对话框
  if (els.dialogTitle) els.dialogTitle.textContent = t('dialog_title');
  if (els.tabPreviewClean) {
    els.tabPreviewClean.textContent = t('tab_clean');
    els.tabPreviewClean.title = t('tab_clean_tip');
  }
  if (els.tabPreviewAnnotated) {
    els.tabPreviewAnnotated.textContent = t('tab_annotated');
    els.tabPreviewAnnotated.title = t('tab_annotated_tip');
  }
  if (els.btnCloseModal) els.btnCloseModal.textContent = t('btn_close');
  if (els.btnDialogClose) els.btnDialogClose.textContent = t('btn_close');
  if (els.btnDownloadSnapshot) els.btnDownloadSnapshot.textContent = t('btn_download_current');
  if (els.btnDownloadAll) els.btnDownloadAll.textContent = t('btn_download_all');

  // 重新渲染构件下拉菜单 (保持选中态与中英分类)
  renderScriptDropdown(els.scriptSearch ? els.scriptSearch.value : '');

  // 重新渲染当前参数面板 (若无参数显示对应语言的空提示)
  refreshParameterPanel();

  // 若弹窗打开，更新文字
  if (currentSnapshots && currentSnapshots.compName) {
    switchPreviewTab(currentSnapshots.activeTab || 'clean');
  }
}

/**
 * 刷新动态参数输入面板
 */
function refreshParameterPanel() {
  const code = els.codeEditor.value;
  const meta = extractScriptMetadata(code);
  currentMetadata = meta;

  els.paramContainer.innerHTML = '';
  if (!meta.params || meta.params.length === 0) {
    els.paramContainer.innerHTML = `<div class="md-empty-tip">${t('params_empty')}</div>`;
    return;
  }

  for (let p of meta.params) {
    const row = document.createElement('div');
    row.className = 'md-param-item';

    const label = document.createElement('label');
    label.className = 'md-param-name';
    label.textContent = p.name;
    label.title = p.description || p.label || p.name;

    const input = document.createElement('input');
    input.className = 'md-text-field';
    input.type = p.type === 'number' ? 'number' : 'text';
    if (p.type === 'number') input.step = 'any';

    const curVal = currentParams[p.name] !== undefined ? currentParams[p.name] : p.defaultValue;
    input.value = curVal !== null ? curVal : '';

    input.addEventListener('change', () => {
      currentParams[p.name] = p.type === 'number' ? Number(input.value) : input.value;
      executeCurrentCode();
    });

    row.appendChild(label);
    row.appendChild(input);
    els.paramContainer.appendChild(row);
  }
}

/**
 * 执行当前 Python 脚本并渲染三维实体
 */
async function executeCurrentCode() {
  if (isRendering) return;
  isRendering = true;
  els.btnRun.classList.add('loading');
  updateStatus(t('loading_modeling'), 'info');

  try {
    const pyCode = els.codeEditor.value;
    const res = await runPlant3dScript(pyCode, currentParams, kernel);

    if (!res.success || !res.shape) {
      throw new Error(getLanguage() === LANG_EN ? 'Script execution produced no valid 3D solid!' : '脚本执行后未产生有效的实体模型！');
    }

    currentShape = res.shape;
    currentSession = res.session;
    currentMetadata = res.meta;

    updateStatus(t('loading_meshing'), 'info');
    const meshData = kernel.meshShape(res.shape, 0.5);

    if (!meshData) {
      throw new Error(getLanguage() === LANG_EN ? 'B-Rep tessellation returned no valid triangles!' : '网格剖分未提取到有效三角面片！');
    }

    renderGeometryToScene(meshData);

    // 计算三维轴测尺寸标注并添加到场景
    const bounds = new THREE.Box3().setFromObject(modelGroup);
    const { dimensionGroup, framingPoints } = create3dDimensionsObject(
      currentSession,
      currentMetadata ? currentMetadata.params : [],
      currentParams,
      bounds
    );

    const oldDim = scene.getObjectByName('CAD_DIMENSIONS_GROUP');
    if (oldDim) scene.remove(oldDim);
    dimensionGroup.visible = false; // 视口交互场景内严格不显示尺寸标注，保持纯净！
    scene.add(dimensionGroup);
    currentFramingPoints = framingPoints;

    fitViewToModel(false);

    const dimCount = currentSession && currentSession.dimensions ? currentSession.dimensions.length : 0;
    const portCount = currentSession && currentSession.ports ? currentSession.ports.length : 0;
    const bboxSize = `${Math.round(meshData.bbox.size[0])} × ${Math.round(meshData.bbox.size[1])} × ${Math.round(meshData.bbox.size[2])} mm`;
    const compTitle = (getLanguage() === LANG_EN ? currentMetadata?.functionName : (res.meta.title || currentMetadata?.functionName)) || 'COMPONENT';

    updateStatus(t('status_model_completed', {
      name: compTitle,
      time: res.executionTimeMs,
      faces: meshData.faceCount,
      triangles: meshData.triangleCount.toLocaleString(),
      bbox: bboxSize,
      ports: portCount,
      dims: dimCount
    }), 'success');
  } catch (err) {
    console.error('建模执行异常:', err);
    updateStatus(t('status_model_error', { msg: err.message }), 'error');
  } finally {
    isRendering = false;
    hideLoading();
  }
}

/**
 * 将剖分网格数据加载至 Three.js 视口
 */
function renderGeometryToScene(meshData) {
  while (modelGroup.children.length > 0) {
    const obj = modelGroup.children[0];
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
      else obj.material.dispose();
    }
    modelGroup.remove(obj);
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(meshData.positions, 3));
  geometry.setIndex(new THREE.BufferAttribute(meshData.indices, 1));
  geometry.computeVertexNormals();

  const material = new THREE.MeshStandardMaterial({
    color: new THREE.Color(modelColor),
    metalness: 0.2,
    roughness: 0.35,
    side: THREE.DoubleSide
  });

  currentMesh = new THREE.Mesh(geometry, material);
  modelGroup.add(currentMesh);

  const edgesGeometry = new THREE.EdgesGeometry(geometry, 24);
  const edgesMaterial = new THREE.LineBasicMaterial({
    color: 0x0f172a, // 浅色视口下使用高对比度深碳墨线 (Slate-900)，轮廓锐利晶莹
    linewidth: 1.5,
    transparent: true,
    opacity: 0.85
  });
  currentEdges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
  modelGroup.add(currentEdges);

  if (currentSession && currentSession.ports) {
    for (let p of currentSession.ports) {
      const origin = new THREE.Vector3(...p.point);
      const dir = new THREE.Vector3(...p.direction).normalize();
      const arrowHelper = new THREE.ArrowHelper(dir, origin, 22, 0xf43f5e, 6, 4);
      modelGroup.add(arrowHelper);
    }
  }

  updateModelRenderMode();
}

function updateModelRenderMode() {
  if (!currentMesh || !currentEdges) return;
  if (renderMode === 'shaded_edges') {
    currentMesh.visible = true;
    currentMesh.material.wireframe = false;
    currentEdges.visible = true;
  } else if (renderMode === 'shaded') {
    currentMesh.visible = true;
    currentMesh.material.wireframe = false;
    currentEdges.visible = false;
  } else if (renderMode === 'wireframe') {
    currentMesh.visible = false;
    currentEdges.visible = true;
  }
}

/**
 * 正交相机自适应居中缩放
 * @param {boolean} includeDimensions 是否将标注外伸端点纳入视景体包围盒
 */
function fitViewToModel(includeDimensions = false) {
  if (!modelGroup || modelGroup.children.length === 0) return;

  const box = new THREE.Box3().setFromObject(modelGroup);
  if (box.isEmpty()) return;

  // 仅在出图带标注尺寸时将尺寸标注外伸端点纳入视景体包围盒，确保尺寸线与文字不被边缘裁剪
  if (includeDimensions && currentFramingPoints && currentFramingPoints.length > 0) {
    for (const pt of currentFramingPoints) {
      box.expandByPoint(new THREE.Vector3(pt[0], pt[1], pt[2]));
    }
  }

  const center = new THREE.Vector3();
  box.getCenter(center);

  const size = new THREE.Vector3();
  box.getSize(size);

  const maxDim = Math.max(size.x, size.y, size.z, 20);
  const width = els.viewportContainer.clientWidth || 800;
  const height = els.viewportContainer.clientHeight || 600;
  const aspect = width / height;

  // 正交相机的视景体跨度：预留工程安全留白
  const viewHeight = maxDim * (includeDimensions ? 1.35 : 1.25);
  camera.left = -viewHeight * aspect / 2;
  camera.right = viewHeight * aspect / 2;
  camera.top = viewHeight / 2;
  camera.bottom = -viewHeight / 2;
  camera.zoom = 1;
  camera.near = -50000;
  camera.far = 50000;
  camera.updateProjectionMatrix();

  controls.target.copy(center);

  // 沿当前视线方向将相机放置在固定距离
  const dir = new THREE.Vector3().subVectors(camera.position, controls.target);
  if (dir.lengthSq() < 0.001) {
    dir.set(1, -1, 1).normalize();
  } else {
    dir.normalize();
  }
  camera.position.copy(center).addScaledVector(dir, 1500);
  controls.update();
}

/**
 * 切换标准工程正交视角 (轴测 / 俯视 / 正视 / 侧视)
 */
function setViewPreset(preset) {
  if (!modelGroup) return;
  const box = new THREE.Box3().setFromObject(modelGroup);
  const center = new THREE.Vector3();
  box.getCenter(center);
  const dist = 1500;

  controls.target.copy(center);

  if (preset === 'iso') {
    // 经典 1:1 工程等轴测视角 (角度 45°, 仰角 35.264°)
    camera.up.set(0, 0, 1);
    camera.position.set(center.x + dist, center.y - dist, center.z + dist);
  } else if (preset === 'top') {
    // 俯视图 (XY 平面)：自顶向下观察，Y 轴在屏幕正上方 (AutoCAD 经典规范)
    camera.up.set(0, 1, 0);
    camera.position.set(center.x, center.y, center.z + dist);
  } else if (preset === 'front') {
    // 正视图 (XZ 平面)：从 -Y 往 +Y 观察，Z 轴在屏幕正上方
    camera.up.set(0, 0, 1);
    camera.position.set(center.x, center.y - dist, center.z);
  } else if (preset === 'side') {
    // 侧视图 (YZ 平面)：从 +X 往 -X 观察，Z 轴在屏幕正上方
    camera.up.set(0, 0, 1);
    camera.position.set(center.x + dist, center.y, center.z);
  }

  camera.updateProjectionMatrix();
  controls.update();

  // 同步分段按钮选中态
  const viewBtns = {
    iso: els.btnIso,
    top: els.btnTop,
    front: els.btnFront,
    side: els.btnSide
  };
  Object.values(viewBtns).forEach(b => b?.classList.remove('active'));
  if (viewBtns[preset]) {
    viewBtns[preset].classList.add('active');
  }
}

/**
 * 生成高清预览图 (严格对齐 pyocc: 纯实体标准轴测图 + 带尺寸标注轴测图双出图)
 */
async function generatePreviewSnapshot() {
  if (!currentMesh) {
    alert(t('alert_no_model'));
    return;
  }

  showLoading(t('loading_snapshot'));
  await new Promise(r => setTimeout(r, 60));

  try {
    const dimGroup = scene.getObjectByName('CAD_DIMENSIONS_GROUP');
    const axes = scene.getObjectByName('CAD_AXES');
    const oldAxesVis = axes ? axes.visible : false;
    if (axes) axes.visible = false;

    const oldBg = scene.background;
    scene.background = new THREE.Color(0xffffff);

    // 出图模式下边线临时切换为深色 0x0f172a (白底黑线，高对比度出图)
    if (currentEdges && currentEdges.material) {
      currentEdges.material.color.set(0x0f172a);
    }

    // 1. 生成纯实体标准轴测出图 (无标注)
    if (dimGroup) dimGroup.visible = false;
    setViewPreset('iso');
    fitViewToModel(false);
    renderer.render(scene, camera);
    const cleanDataURL = renderer.domElement.toDataURL('image/png', 1.0);

    // 2. 生成带工程尺寸标注的轴测图
    if (dimGroup) dimGroup.visible = true;
    setViewPreset('iso');
    fitViewToModel(true);
    renderer.render(scene, camera);
    const annotatedDataURL = renderer.domElement.toDataURL('image/png', 1.0);

    // 恢复视口场景状态 (视口内不显示尺寸标注，边线保持深色墨线)
    if (dimGroup) dimGroup.visible = false;
    if (currentEdges && currentEdges.material) {
      currentEdges.material.color.set(0x0f172a);
    }
    scene.background = oldBg;
    if (axes) axes.visible = oldAxesVis;
    fitViewToModel(false);
    renderer.render(scene, camera);

    showSnapshotModal(cleanDataURL, annotatedDataURL);
  } finally {
    hideLoading();
  }
}

/**
 * 展示三维出图预览对话框 (支持标准轴测与尺寸标注双选项卡切换)
 */
function showSnapshotModal(cleanDataURL, annotatedDataURL) {
  const compName = currentMetadata?.functionName || 'COMPONENT';
  currentSnapshots = {
    clean: cleanDataURL,
    annotated: annotatedDataURL,
    activeTab: 'clean',
    compName
  };

  switchPreviewTab('clean');

  els.btnDownloadSnapshot.onclick = () => {
    const isClean = currentSnapshots.activeTab === 'clean';
    const url = isClean ? currentSnapshots.clean : currentSnapshots.annotated;
    const suffix = isClean ? 'clean' : 'annotated';
    downloadFile(url, `${compName}_${suffix}.png`);
  };

  els.btnDownloadAll.onclick = () => {
    downloadFile(currentSnapshots.clean, `${compName}_clean.png`);
    setTimeout(() => {
      downloadFile(currentSnapshots.annotated, `${compName}_annotated.png`);
    }, 250);
  };

  els.snapshotModal.classList.remove('hidden');
}

/**
 * 切换出图预览选项卡
 */
function switchPreviewTab(tabKey) {
  currentSnapshots.activeTab = tabKey;
  const w = renderer ? renderer.domElement.width : 1440;
  const h = renderer ? renderer.domElement.height : 671;
  const name = currentSnapshots.compName || 'COMPONENT';

  if (tabKey === 'clean') {
    els.tabPreviewClean?.classList.add('active');
    els.tabPreviewAnnotated?.classList.remove('active');
    els.snapshotImg.src = currentSnapshots.clean;
    els.snapshotInfo.textContent = t('snapshot_meta_clean', { name, w, h });
  } else {
    els.tabPreviewClean?.classList.remove('active');
    els.tabPreviewAnnotated?.classList.add('active');
    els.snapshotImg.src = currentSnapshots.annotated;
    els.snapshotInfo.textContent = t('snapshot_meta_annotated', { name, w, h });
  }
}

function downloadFile(dataURL, filename) {
  const a = document.createElement('a');
  a.href = dataURL;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * 底部多行控制台日志输出与状态管理 (无图标无 emoji，规范时间戳)
 */
function updateStatus(msg, type = 'info') {
  const now = new Date();
  const timeStr = [
    String(now.getHours()).padStart(2, '0'),
    String(now.getMinutes()).padStart(2, '0'),
    String(now.getSeconds()).padStart(2, '0')
  ].join(':');

  if (els.logList) {
    const entry = document.createElement('div');
    entry.className = 'md-log-entry';

    const timeEl = document.createElement('span');
    timeEl.className = 'md-log-time';
    timeEl.textContent = `[${timeStr}]`;

    const isEn = getLanguage() === LANG_EN;
    const tagEl = document.createElement('span');
    tagEl.className = `md-log-tag ${type === 'error' ? 'err' : (type === 'success' ? 'ok' : (type === 'warn' ? 'warn' : 'info'))}`;
    tagEl.textContent = type === 'error' ? (isEn ? '[ERROR]' : '[错误]') : (type === 'success' ? (isEn ? '[OK]' : '[成功]') : (type === 'warn' ? (isEn ? '[WARN]' : '[警告]') : (isEn ? '[INFO]' : '[信息]')));

    const msgEl = document.createElement('span');
    msgEl.className = `md-log-msg ${type === 'success' || type === 'error' ? 'highlight' : ''}`;
    msgEl.textContent = msg;

    entry.appendChild(timeEl);
    entry.appendChild(tagEl);
    entry.appendChild(msgEl);

    els.logList.appendChild(entry);
    els.logList.scrollTop = els.logList.scrollHeight;
  }

  if (els.statusQuick) {
    els.statusQuick.textContent = `[${timeStr}] ${msg}`;
    if (type === 'error') {
      els.statusQuick.classList.add('error');
    } else {
      els.statusQuick.classList.remove('error');
    }
  }

  if (els.logStatusBadge) {
    els.logStatusBadge.className = `md-badge md-badge-${type === 'error' ? 'error' : (type === 'success' ? 'success' : 'info')}`;
    els.logStatusBadge.textContent = type === 'error' ? t('badge_error') : (type === 'success' ? t('badge_ready') : t('badge_running'));
  }
}
