"""
一键更新发音音频：生成新单词音频 + 上传到 COS。
用法：python update_audio.py

首次使用需要配置 coscmd（只需一次）：
  coscmd config -a <SecretId> -s <SecretKey> -b dailyvacu-1323718537 -r ap-guangzhou

SecretId/SecretKey 在腾讯云控制台 → 访问管理 → API 密钥管理 中获取。
"""
import asyncio
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

import edge_tts

VOICE = "en-US-AriaNeural"
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "index.html")


def extract_words():
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    words = re.findall(r"word:'([^']+)'", content)
    words += re.findall(r'word:"([^"]+)"', content)
    seen = set()
    unique = []
    for w in words:
        w_lower = w.lower()
        if w_lower not in seen:
            seen.add(w_lower)
            unique.append(w)
    return unique


async def generate_one(word, sem):
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


async def generate_audio(words):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    existing = {f[:-4] for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")} if os.path.exists(AUDIO_DIR) else set()
    new_words = [w for w in words if w.lower().replace(" ", "_").replace("-", "_") not in existing]

    if not new_words:
        print(f"音频已就绪，共 {len(existing)} 个，无需新增。")
        return 0

    print(f"需生成 {len(new_words)} 个新音频...")
    sem = asyncio.Semaphore(5)
    tasks = [generate_one(w, sem) for w in new_words]
    ok = 0
    for coro in asyncio.as_completed(tasks):
        word, status = await coro
        if status == "ok":
            ok += 1
            print(f"  {word} OK")
        elif status != "skip":
            print(f"  {word} FAIL: {status}")
    print(f"生成完成: 新增 {ok} 个")
    return ok


def upload_to_cos():
    """用 coscmd 上传 audio/ 目录到 COS"""
    print("上传音频到 COS...")
    try:
        result = subprocess.run(
            ["coscmd", "upload", "-r", AUDIO_DIR, "/audio/"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode == 0:
            print("上传完成!")
        else:
            print(f"上传失败: {result.stderr}")
            print("请先配置 coscmd: coscmd config -a <SecretId> -s <SecretKey> -b dailyvacu-1323718537 -r ap-guangzhou")
    except FileNotFoundError:
        print("coscmd 未安装，请运行: pip install coscmd")


async def main():
    words = extract_words()
    print(f"词库共 {len(words)} 个唯一单词")

    new_count = await generate_audio(words)

    if new_count > 0:
        upload = input("是否上传到 COS? (y/n): ").strip().lower()
        if upload == 'y':
            upload_to_cos()
        else:
            print(f"跳过上传。音频目录: {AUDIO_DIR}")
            print("手动上传: coscmd upload -r audio/ /audio/")


if __name__ == "__main__":
    asyncio.run(main())
