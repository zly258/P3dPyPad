// -*- coding: utf-8 -*-
/**
 * P3dPyPad Web - 原生高性能 Node.js 本地开发与预览服务器
 * 零第三方外部依赖，基于 Node.js 内置 http / fs / path 模块构建
 * 支持 WebAssembly (application/wasm)、ES 模块及 Cross-Origin 隔离响应头
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { syncPyScripts } from './sync_pyscripts.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 启动时确保 pyscripts 资产清单完整
const manifestFile = path.join(__dirname, 'public/pyscripts_manifest.json');
if (!fs.existsSync(manifestFile)) {
  try {
    syncPyScripts();
  } catch (e) {
    console.warn('提示: 同步 pyscripts 发生警告:', e.message);
  }
}

// 静态文件 MIME 类型映射字典
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.wasm': 'application/wasm',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
  '.py': 'text/plain; charset=utf-8'
};

const DEFAULT_PORT = parseInt(process.env.PORT, 10) || 3000;
const HOST = '127.0.0.1';

/**
 * 创建 HTTP 静态文件请求处理服务
 */
const server = http.createServer((req, res) => {
  // 1. 设置跨域与 WebAssembly 线程隔离必需的响应头
  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  res.setHeader('Cross-Origin-Embedder-Policy', 'credentialless');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.statusCode = 405;
    res.end('Method Not Allowed');
    return;
  }

  // 2. 解析请求路径
  const parsedUrl = new URL(req.url, `http://${req.headers.host || HOST}`);
  let pathname = decodeURIComponent(parsedUrl.pathname);

  // 默认根路径指向 index.html
  if (pathname === '/' || pathname === '') {
    pathname = '/index.html';
  }

  const filePath = path.normalize(path.join(__dirname, pathname));

  // 安全检查：防止路径跨目录穿越
  if (!filePath.startsWith(__dirname)) {
    res.statusCode = 403;
    res.end('Forbidden');
    return;
  }

  // 3. 检查文件状态并返回流
  fs.stat(filePath, (err, stats) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.statusCode = 404;
        res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        res.end(`404 未找到资源: ${pathname}`);
      } else {
        res.statusCode = 500;
        res.end(`500 服务器错误: ${err.message}`);
      }
      return;
    }

    if (stats.isDirectory()) {
      // 目录尝试重定向到该目录下的 index.html
      const indexPath = path.join(filePath, 'index.html');
      if (fs.existsSync(indexPath)) {
        serveFile(indexPath, res);
      } else {
        res.statusCode = 403;
        res.end('Directory listing forbidden');
      }
      return;
    }

    serveFile(filePath, res);
  });
});

function serveFile(filePath, res) {
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  res.statusCode = 200;
  res.setHeader('Content-Type', contentType);

  const stream = fs.createReadStream(filePath);
  stream.on('error', err => {
    res.statusCode = 500;
    res.end(`流读取错误: ${err.message}`);
  });
  stream.pipe(res);
}

/**
 * 端口自动探测与启动监听
 */
function startServer(port) {
  server.listen(port, HOST, () => {
    console.log('----------------------------------------------------');
    console.log(' P3dPyPad Web 离线仿真与三维预览工作台已启动');
    console.log(` 本地访问地址: http://${HOST}:${port}/`);
    console.log(' 静态资源根目录:', __dirname);
    console.log(' 按 Ctrl+C 可停止服务器');
    console.log('----------------------------------------------------');
  });

  server.on('error', err => {
    if (err.code === 'EADDRINUSE') {
      console.log(`提示: 端口 ${port} 已被占用，正在尝试端口 ${port + 1}...`);
      startServer(port + 1);
    } else {
      console.error('服务器启动失败:', err);
    }
  });
}

startServer(DEFAULT_PORT);
