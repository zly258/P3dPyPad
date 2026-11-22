using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace P3dPyPad
{
    /// <summary>
    /// 轻量的用户偏好持久化（%APPDATA%\P3dPyPad\settings.json）。
    ///
    /// 只存「上次用过的东西」——目录、勾选状态这类，不存业务数据。
    /// 语言选项沿用 LocalizationManager 自己的读写，这里不接管，避免两处写入互相覆盖：
    /// 每次保存都先把文件里已有的键读出来合并，再整体写回。
    /// </summary>
    internal static class UserSettings
    {
        private static readonly string SettingsDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "P3dPyPad");

        private static readonly string SettingsFile = Path.Combine(SettingsDir, "settings.json");

        private static readonly object Sync = new object();

        public static string Get(string key, string fallback = null)
        {
            if (string.IsNullOrEmpty(key)) return fallback;
            lock (Sync)
            {
                var map = ReadAll();
                string value;
                return map.TryGetValue(key, out value) && !string.IsNullOrEmpty(value) ? value : fallback;
            }
        }

        public static void Set(string key, string value)
        {
            if (string.IsNullOrEmpty(key)) return;
            lock (Sync)
            {
                var map = ReadAll();
                if (string.IsNullOrEmpty(value)) map.Remove(key);
                else map[key] = value;
                WriteAll(map);
            }
        }

        /// <summary>
        /// 读一个目录类偏好。只在目录仍然存在时才返回，否则视为无效并回退到默认值——
        /// 避免用户删掉了目录、下次打开却停在一个不存在的路径上。
        /// </summary>
        public static string GetDirectory(string key, string fallback = null)
        {
            var saved = Get(key);
            return !string.IsNullOrEmpty(saved) && Directory.Exists(saved) ? saved : fallback;
        }

        private static Dictionary<string, string> ReadAll()
        {
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            try
            {
                if (!File.Exists(SettingsFile)) return map;
                var text = File.ReadAllText(SettingsFile, Encoding.UTF8);
                foreach (var kv in ParseFlatJson(text))
                {
                    map[kv.Key] = kv.Value;
                }
            }
            catch
            {
                // 设置文件损坏时退回默认值，不影响启动。
            }
            return map;
        }

        private static void WriteAll(Dictionary<string, string> map)
        {
            try
            {
                Directory.CreateDirectory(SettingsDir);
                var sb = new StringBuilder();
                sb.Append("{\n");
                var first = true;
                foreach (var kv in map)
                {
                    if (!first) sb.Append(",\n");
                    first = false;
                    sb.Append("  \"").Append(Escape(kv.Key)).Append("\": \"")
                      .Append(Escape(kv.Value)).Append('"');
                }
                sb.Append("\n}\n");
                File.WriteAllText(SettingsFile, sb.ToString(), new UTF8Encoding(false));
            }
            catch
            {
                // 写失败（只读环境等）时静默忽略，下次打开只是回到默认目录。
            }
        }

        /// <summary>
        /// 解析扁平 JSON（一层键值对）。设置文件只有这种结构，
        /// 不引入 JSON 依赖，也避免 Newtonsoft 与 AutoCAD 自带版本冲突。
        /// </summary>
        private static IEnumerable<KeyValuePair<string, string>> ParseFlatJson(string text)
        {
            var i = 0;
            while (i < text.Length)
            {
                var keyStart = text.IndexOf('"', i);
                if (keyStart < 0) break;
                var keyEnd = FindStringEnd(text, keyStart + 1);
                if (keyEnd < 0) break;

                var colon = text.IndexOf(':', keyEnd);
                if (colon < 0) break;

                var valueStart = text.IndexOf('"', colon);
                if (valueStart < 0) break;
                var valueEnd = FindStringEnd(text, valueStart + 1);
                if (valueEnd < 0) break;

                var key = Unescape(text.Substring(keyStart + 1, keyEnd - keyStart - 1));
                var value = Unescape(text.Substring(valueStart + 1, valueEnd - valueStart - 1));
                yield return new KeyValuePair<string, string>(key, value);

                i = valueEnd + 1;
            }
        }

        private static int FindStringEnd(string text, int from)
        {
            for (var i = from; i < text.Length; i++)
            {
                if (text[i] == '\\') { i++; continue; }
                if (text[i] == '"') return i;
            }
            return -1;
        }

        private static string Escape(string s)
        {
            if (string.IsNullOrEmpty(s)) return string.Empty;
            return s.Replace("\\", "\\\\").Replace("\"", "\\\"");
        }

        private static string Unescape(string s)
        {
            if (string.IsNullOrEmpty(s)) return string.Empty;
            return s.Replace("\\\"", "\"").Replace("\\\\", "\\");
        }
    }
}
