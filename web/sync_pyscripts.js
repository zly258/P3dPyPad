// -*- coding: utf-8 -*-
/**
 * AutoCAD Plant 3D 构件资产同步与目录索引生成器
 * 将 pyscripts/ 资产同步至 web/public/pyscripts/ 并构建分类索引 manifest.json
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const srcDir = path.resolve(__dirname, '../pyscripts');
const dstDir = path.resolve(__dirname, 'public/pyscripts');
const manifestPath = path.resolve(__dirname, 'public/pyscripts_manifest.json');

const CATEGORY_MAP = {
  'custom_scripts/01_pipe_fittings': '01 管道管件 (Pipe Fittings)',
  'custom_scripts/02_flanges_gaskets': '02 法兰垫片 (Flanges & Gaskets)',
  'custom_scripts/03_valves': '03 阀门类 (Valves)',
  'custom_scripts/04_instruments': '04 仪表构件 (Instruments)',
  'custom_scripts/05_supports': '05 定制支吊架 (Custom Supports)',
  'custom_scripts/06_equipment': '06 工艺设备 (Equipment)',
  'supports/cd_zd2010': '07 电力标准 CD/ZD 2010 支吊架',
  'supports/hgt_21629': '08 化工标准 HG/T 21629 支架'
};

function copyRecursive(src, dst) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (!fs.existsSync(dst)) fs.mkdirSync(dst, { recursive: true });
    for (const child of fs.readdirSync(src)) {
      copyRecursive(path.join(src, child), path.join(dst, child));
    }
  } else {
    fs.copyFileSync(src, dst);
  }
}

function scanAndBuildManifest(dir, rel = '') {
  let list = [];
  if (!fs.existsSync(dir)) return list;

  for (const item of fs.readdirSync(dir)) {
    // 排除系统脚本目录，不计入 manifest
    if (item === 'system_defaults') continue;
    const full = path.join(dir, item);
    const subRel = rel ? `${rel}/${item}` : item;
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      list = list.concat(scanAndBuildManifest(full, subRel));
    } else if (item.endsWith('.py')) {
      const content = fs.readFileSync(full, 'utf-8');
      const filename = path.basename(item, '.py');
      let title = filename;
      let desc = '';

      const actMatch = content.match(/@activate\s*\(([\s\S]*?)\)/);
      if (actMatch) {
        const sMatch = actMatch[1].match(/TooltipShort\s*=\s*[uU]?["']([^"']+)["']/);
        const lMatch = actMatch[1].match(/TooltipLong\s*=\s*[uU]?["']([^"']+)["']/);
        if (sMatch) title = sMatch[1];
        if (lMatch) desc = lMatch[1];
      }

      const normRel = subRel.replace(/\\/g, '/');
      const dirKey = Object.keys(CATEGORY_MAP).find(k => normRel.startsWith(k));
      const catName = dirKey ? CATEGORY_MAP[dirKey] : '其他构件';

      list.push({
        id: normRel,
        filename: item,
        name: filename,
        title: title !== filename ? `${filename} (${title})` : filename,
        category: catName,
        path: `public/pyscripts/${normRel}`,
        description: desc
      });
    }
  }
  return list;
}

export function syncPyScripts() {
  console.log('正在同步 pyscripts/ 资产到 web/public/pyscripts/...');
  copyRecursive(srcDir, dstDir);
  console.log('正在解析并生成 pyscripts_manifest.json 资产清单...');
  const allScripts = scanAndBuildManifest(dstDir);
  fs.writeFileSync(manifestPath, JSON.stringify(allScripts, null, 2), 'utf-8');
  console.log(`同步完成！共索引 ${allScripts.length} 个参数化构件脚本资产。`);
  return allScripts;
}

// 允许命令行直接执行
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  syncPyScripts();
}
