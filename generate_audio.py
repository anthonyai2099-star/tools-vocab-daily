"""
批量生成单词发音音频（MP3）。
用法：python generate_audio.py
首次运行生成所有单词，之后只生成新增单词的音频。
生成的文件在 audio/ 目录下，需上传到 COS。
"""
import asyncio
import json
import os
import re
import sys

# Windows 控制台 UTF-8 输出
sys.stdout.reconfigure(encoding="utf-8")

import edge_tts

VOICE = "en-US-AriaNeural"  # 美式英语女声，音质好
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "index.html")


def extract_words():
    """从 index.html 中提取所有唯一单词"""
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 word:'xxx' 或 word:"xxx"
    words = re.findall(r"word:'([^']+)'", content)
    words += re.findall(r'word:"([^"]+)"', content)

    # 去重，保持顺序
    seen = set()
    unique = []
    for w in words:
        w_lower = w.lower()
        if w_lower not in seen:
            seen.add(w_lower)
            unique.append(w)
    return unique


async def generate_one(word, sem):
    """生成单个单词的音频"""
    filename = word.lower().replace(" ", "_").replace("-", "_") + ".mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return word, "skip"

    async with sem:
        try:
            tts = edge_tts.Communicate(word, VOICE)
            await tts.save(filepath)
            return word, "ok"
        except Exception as e:
            return word, f"error: {e}"


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)

    words = extract_words()
    print(f"词库共有 {len(words)} 个唯一单词")

    # 检查已有音频
    existing = set()
    if os.path.exists(AUDIO_DIR):
        existing = {f[:-4] for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")}

    new_words = [w for w in words if w.lower().replace(" ", "_").replace("-", "_") not in existing]
    print(f"已有音频: {len(existing)} 个，需生成: {len(new_words)} 个")

    if not new_words:
        print("所有音频已就绪，无需生成。")
        return

    # 并发生成，限制并发数避免被限流
    sem = asyncio.Semaphore(5)
    tasks = [generate_one(w, sem) for w in new_words]

    ok_count = 0
    skip_count = 0
    err_count = 0

    for i, coro in enumerate(asyncio.as_completed(tasks)):
        word, status = await coro
        if status == "ok":
            ok_count += 1
            print(f"  [{i+1}/{len(new_words)}] {word} OK")
        elif status == "skip":
            skip_count += 1
        else:
            err_count += 1
            print(f"  [{i+1}/{len(new_words)}] {word} FAIL: {status}")

    print(f"\n完成: 新增 {ok_count} 个, 跳过 {skip_count} 个, 失败 {err_count} 个")
    print(f"音频目录: {AUDIO_DIR}")
    print(f"请将 audio/ 目录上传到 COS 根目录下。")


if __name__ == "__main__":
    asyncio.run(main())
