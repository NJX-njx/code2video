# 导入操作系统相关功能，用于文件路径操作
import os
# 导入JSON处理模块，用于读写JSON格式的故事板文件
import json
# 导入命令行参数解析模块，用于处理用户输入的命令行参数
import argparse
# 导入子进程模块，用于执行Manim渲染命令
import subprocess
# 从agents模块导入故事板生成函数
from mathvideo.agents.planner import generate_storyboard
# 从agents模块导入代码生成和修复函数
from mathvideo.agents.coder import generate_code, fix_code, refine_code
from mathvideo.agents.asset_manager import AssetManager
from mathvideo.agents.critic import VisualCritic
# 导入任务类型路由器
from mathvideo.agents.router import classify_task, get_section_mode
from mathvideo.config import USE_VISUAL_FEEDBACK
from mathvideo.utils import make_slug, rename_project_dir


def main():
    """
    主函数：自动数学视频生成器的入口点

    功能流程：
    1. 解析命令行参数（文本/图片与是否渲染）
    2. 创建输出目录结构
    3. 生成故事板（storyboard）
    4. 为每个章节生成Manim代码
    5. 如果指定了--render参数，则渲染视频（带自动错误修复）

    命令行参数:
        prompt: 要讲解的数学主题/问题/描述（可选，若仅使用图片可留空）
        --image: 输入图片路径（可多次传入）
        --render: 是否立即渲染视频（可选标志）

    输出结构:
        output/
          {topic_slug}/
            storyboard.json      # 故事板JSON文件
            scripts/             # 生成的Python脚本目录
              section_1.py
              section_2.py
              ...
            media/               # 渲染后的视频文件目录
    """
    # 创建命令行参数解析器，设置程序描述
    parser = argparse.ArgumentParser(description="Auto Math Video Generator")
    # 添加可选位置参数：主题/问题/描述（允许为空，配合图片输入）
    parser.add_argument(
        "prompt",
        nargs="?",
        default="",
        help="数学主题/知识点/问题/描述（可选，若仅使用图片可留空）",
    )
    # 可选图片输入（可重复传入）
    parser.add_argument(
        "-i",
        "--image",
        action="append",
        default=[],
        help="输入图片路径（可多次传入）",
    )
    # 添加可选标志参数：是否渲染视频
    parser.add_argument("--render", action="store_true", help="Render the video using Manim")
    # Web 后端指定输出目录（跳过 slug 生成，直接使用后端已准备好的目录）
    parser.add_argument(
        "--output-dir",
        default="",
        help="指定输出目录路径（由 Web 后端传入，跳过 slug 生成）",
    )
    # 解析命令行参数并存储到args对象中
    args = parser.parse_args()

    # 创建结构化的输出目录
    # 输入校验：至少提供文本或图片
    if not args.prompt.strip() and not args.image:
        print("❌ 请提供文本输入或图片输入（或两者）。")
        raise SystemExit(1)

    # 如果后端已指定输出目录，直接使用；否则自行生成 slug
    if args.output_dir:
        base_output_dir = args.output_dir
        topic_slug = os.path.basename(base_output_dir)
    else:
        # 生成项目 slug（对长文本做截断+哈希）
        image_hint = ",".join([os.path.basename(p) for p in args.image]) if args.image else None
        topic_slug = make_slug(args.prompt.strip() or "image-input", extra=image_hint)
        base_output_dir = os.path.join("output", topic_slug)
    # 构建脚本目录路径：用于存储生成的Python代码文件
    scripts_dir = os.path.join(base_output_dir, "scripts")
    # 构建媒体目录路径：用于存储渲染后的视频文件
    media_dir = os.path.join(base_output_dir, "media")

    # 创建脚本目录（如果不存在则创建，存在则不报错）
    os.makedirs(scripts_dir, exist_ok=True)
    # 创建媒体目录（如果不存在则创建，存在则不报错）
    os.makedirs(media_dir, exist_ok=True)

    # 打印项目启动信息
    print(f"🚀 Starting project: {args.prompt or '（仅图片输入）'}")
    # 打印输出目录路径
    print(f"📂 Output directory: {base_output_dir}")

    # 步骤0：处理输入图片（可选）
    input_image_paths = []
    if args.image:
        inputs_dir = os.path.join(base_output_dir, "inputs")
        os.makedirs(inputs_dir, exist_ok=True)
        for idx, img_path in enumerate(args.image, start=1):
            if not os.path.exists(img_path):
                print(f"⚠️ 图片不存在，已跳过: {img_path}")
                continue
            # 复制到项目输入目录，避免后续路径丢失
            safe_name = os.path.basename(img_path) or f"input_{idx}.png"
            target_path = os.path.join(inputs_dir, safe_name)
            try:
                import shutil
                if os.path.abspath(img_path) == os.path.abspath(target_path):
                    input_image_paths.append(target_path)
                else:
                    shutil.copy2(img_path, target_path)
                    input_image_paths.append(target_path)
            except Exception as e:
                print(f"⚠️ 图片复制失败: {img_path} ({e})")

    # 步骤0.5：任务类型路由（在生成故事板之前先判断任务类型）
    # 先对图片进行理解（如果有的话），因为图片内容会影响任务分类
    image_context_for_router = None
    if input_image_paths:
        from mathvideo.agents.planner import describe_images
        image_context_for_router = describe_images(input_image_paths)
    
    task_type = classify_task(args.prompt.strip(), image_context=image_context_for_router)
    section_mode = get_section_mode(task_type)
    print(f"📊 Section 模式: {section_mode}")

    # 步骤1：生成故事板（根据任务类型选择不同的 Prompt 模板）
    storyboard = generate_storyboard(
        args.prompt.strip(),
        image_paths=input_image_paths,
        task_type=task_type,
    )
    # 检查故事板是否生成成功
    if not storyboard:
        # 如果生成失败，打印错误信息并退出程序
        print("❌ Failed to generate storyboard.")
        raise SystemExit(1)

    # 步骤1.1: 用 AI 生成的 topic 重命名项目文件夹（让文件夹名有意义）
    ai_topic = storyboard.get("topic", "").strip()
    if ai_topic:
        new_slug = make_slug(ai_topic)
        new_base_dir = rename_project_dir(base_output_dir, new_slug)
        if new_base_dir != base_output_dir:
            print(f"📁 项目重命名: {os.path.basename(base_output_dir)} → {os.path.basename(new_base_dir)}")
            base_output_dir = new_base_dir
            scripts_dir = os.path.join(base_output_dir, "scripts")
            media_dir = os.path.join(base_output_dir, "media")
            topic_slug = os.path.basename(base_output_dir)

    # 构建故事板JSON文件的保存路径
    storyboard_path = os.path.join(base_output_dir, "storyboard.json")
    # 以写入模式打开文件，使用UTF-8编码
    with open(storyboard_path, "w", encoding="utf-8") as f:
        # 将故事板字典写入JSON文件，使用2个空格缩进，保留中文字符
        json.dump(storyboard, f, indent=2, ensure_ascii=False)
    # 打印成功保存的信息
    print(f"✅ Storyboard saved to {storyboard_path}")

    # 步骤1.5: 资产增强 (Code2Video 借鉴)
    # 初始化资产管理器，指定资产下载目录
    assets_dir = os.path.join(base_output_dir, "assets")
    asset_manager = AssetManager(assets_dir)
    # 分析故事板并下载所需资产，更新故事板数据
    storyboard = asset_manager.process(storyboard)

    # 保存更新后的故事板（包含资产信息）
    with open(storyboard_path, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)
    print("✅ Enhanced storyboard saved")

    # 步骤2：为每个章节生成代码
    # 递进模式下，当前 Section 的代码会作为下一个 Section 的上下文
    previous_section_code = ""  # 用于递进模式的上下文传递
    rendered_videos = []  # 收集所有成功渲染的视频路径，用于最终合并
    # 遍历故事板中的所有章节
    for section in storyboard.get("sections", []):
        # 打印当前正在处理的章节ID
        print(f"\n🔄 Processing section: {section['id']}")
        # 调用LLM生成该章节的Manim代码
        # 递进模式下传入前序代码作为上下文
        code, class_name = generate_code(
            section,
            previous_code=previous_section_code if section_mode == "sequential" else "",
            task_type=task_type,
        )

        # 检查代码是否生成成功
        if code:
            # 构建Python脚本文件的保存路径，使用章节ID作为文件名
            filename = os.path.join(scripts_dir, f"{section['id']}.py")
            # 以写入模式打开文件
            with open(filename, "w", encoding="utf-8") as f:
                # 将生成的代码写入文件
                f.write(code)
            # 打印代码保存成功的信息
            print(f"💻 Code saved to {filename}")
            
            # 递进模式下，保存当前 Section 的代码供下一个 Section 使用
            if section_mode == "sequential":
                previous_section_code = code

            # 步骤3：如果用户指定了--render参数，则渲染视频
            if args.render:
                # 打印开始渲染的信息
                print(f"🎬 Rendering {class_name}...")
                # 复制当前环境变量，以便修改PYTHONPATH而不影响原环境
                env = os.environ.copy()
                # 设置PYTHONPATH为当前工作目录，确保可以导入mathvideo.manim_base模块
                env["PYTHONPATH"] = os.getcwd()

                # 输出到指定的媒体目录
                # 使用sys.executable -m manim确保使用正确的Python环境
                import sys
                # 构建Manim渲染命令：
                # - sys.executable: 当前Python解释器
                # - "-m manim": 以模块方式运行manim
                # - "-ql": 低质量快速渲染（用于测试）
                # - "--media_dir": 指定媒体输出目录
                # - filename: 要渲染的Python脚本文件
                # - class_name: 要渲染的场景类名
                cmd = [sys.executable, "-m", "manim", "-ql", "--media_dir", media_dir, filename, class_name]

                # 设置最大重试次数为3次（总共尝试4次：0, 1, 2, 3）
                max_retries = 3
                # 循环尝试渲染，最多重试max_retries次
                for attempt in range(max_retries + 1):
                    try:
                        # 运行Manim渲染命令
                        # check=True: 如果命令返回非零退出码则抛出异常
                        # env=env: 使用修改后的环境变量
                        # cwd=os.getcwd(): 设置工作目录为当前目录
                        # capture_output=True: 捕获标准输出和标准错误
                        # text=True: 以文本模式返回输出（而不是字节）
                        result = subprocess.run(cmd, check=True, env=env, cwd=os.getcwd(), capture_output=True, text=True, encoding='utf-8', errors='replace')
                        # 渲染成功，打印成功信息
                        print(f"✨ Rendered {class_name} successfully.")

                        # 步骤4: 视觉反馈与优化 (Refiner Loop)
                        if USE_VISUAL_FEEDBACK:
                            # 构造视频文件路径 (Manim默认结构: media/videos/脚本名/质量/类名.mp4)
                            # -ql 对应 480p15
                            script_name = os.path.splitext(os.path.basename(filename))[0]
                            video_path = os.path.join(media_dir, "videos", script_name, "480p15", f"{class_name}.mp4")

                            if os.path.exists(video_path):
                                print(f"👁️ analyzing video frame: {video_path}")
                                critic = VisualCritic()
                                suggestion = critic.critique(video_path, section)

                                if suggestion:
                                    print(f"🎨 Suggestion: {suggestion}")
                                    print("🔧 Refining code...")

                                    # 读取当前代码
                                    with open(filename, "r", encoding="utf-8") as f:
                                        current_code = f.read()

                                    # 调用优化代理
                                    refined_code = refine_code(current_code, suggestion)

                                    if refined_code:
                                        # 保存并重试
                                        with open(filename, "w", encoding="utf-8") as f:
                                            f.write(refined_code)

                                        print("♻️ Re-rendering refined code...")
                                        try:
                                            # 只重试一次渲染
                                            subprocess.run(cmd, check=True, env=env, cwd=os.getcwd(), capture_output=True, text=True, encoding='utf-8', errors='replace')
                                            print("✨ Refined render success!")
                                        except subprocess.CalledProcessError as e:
                                            print(f"❌ Refined render failed: {e.stderr}")
                                else:
                                    print("✅ Visual check passed!")
                            else:
                                print(f"⚠️ Video not found: {video_path}")

                        # 记录成功渲染的视频路径
                        script_name_for_path = os.path.splitext(os.path.basename(filename))[0]
                        rendered_path = os.path.join(media_dir, "videos", script_name_for_path, "480p15", f"{class_name}.mp4")
                        if os.path.exists(rendered_path):
                            rendered_videos.append(rendered_path)

                        # 跳出重试循环
                        break  # Success!
                    except subprocess.CalledProcessError as e:
                        # 渲染失败，打印失败信息（包含尝试次数）
                        print(f"❌ Failed to render {class_name} (Attempt {attempt + 1}/{max_retries + 1})")
                        # 获取错误输出信息
                        error_output = e.stderr or e.stdout or "（无错误输出）"
                        # 打印错误详情（只显示最后500个字符，避免输出过长）
                        print(f"Error details:\n{error_output[-500:]}...")

                        # 如果还有重试机会
                        if attempt < max_retries:
                            # 打印尝试自动修复代码的信息
                            print("🔧 Attempting to self-correct code...")

                            # 读取当前出错的代码文件
                            with open(filename, "r", encoding="utf-8") as f:
                                current_code = f.read()

                            # 调用LLM修复代码，传入当前代码和错误信息
                            fixed_code = fix_code(current_code, error_output)

                            # 检查是否成功生成修复后的代码
                            if fixed_code:
                                # 将修复后的代码写回文件
                                with open(filename, "w", encoding="utf-8") as f:
                                    f.write(fixed_code)
                                # 打印修复成功信息，准备重试
                                print(f"📝 Fixed code saved to {filename}. Retrying...")
                            else:
                                # 无法生成修复代码，停止重试
                                print("❌ Could not generate fixed code. Stopping retries.")
                                break
                        else:
                            # 已达到最大重试次数，放弃当前章节，继续处理下一个
                            print("❌ Max retries reached. Moving to next section.")

    # 步骤5：合并所有分镜视频为一个完整视频
    if args.render and len(rendered_videos) > 1:
        print(f"\n🎬 正在合并 {len(rendered_videos)} 个分镜视频...")
        final_video = _merge_videos(rendered_videos, base_output_dir)
        if final_video:
            print(f"✨ 完整视频已生成: {final_video}")
        else:
            print("⚠️ 视频合并失败，各分镜视频仍可单独播放")
    elif args.render and len(rendered_videos) == 1:
        # 只有一个视频，直接复制为最终视频
        import shutil
        final_path = os.path.join(base_output_dir, "final_video.mp4")
        shutil.copy2(rendered_videos[0], final_path)
        print(f"✨ 最终视频: {final_path}")

    print(f"\n✅ 项目完成: {base_output_dir}")


def _merge_videos(video_paths: list, output_dir: str) -> str:
    """
    将多个分镜视频合并为一个完整视频。

    优先使用 PyAV（Manim 已安装的依赖）的 concat 模式进行快速拼接。
    如果 PyAV 不可用，回退尝试 CLI ffmpeg。

    参数:
        video_paths: 按顺序排列的视频文件路径列表
        output_dir: 输出目录

    返回:
        str: 合并后的视频文件路径，或失败时返回 None
    """
    import shutil
    from pathlib import Path

    final_path = os.path.join(output_dir, "final_video.mp4")

    # 方式1: 使用 PyAV（Manim 的 ffmpeg 绑定），与 Manim 自身的合并方式一致
    try:
        import av

        # 创建 concat 文件列表（与 Manim 的 combine_files 格式一致）
        concat_list_path = os.path.join(output_dir, "_concat_list.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            f.write("# This file is used internally for video concatenation.\n")
            for vp in video_paths:
                posix_path = Path(vp).resolve().as_posix()
                f.write(f"file 'file:{posix_path}'\n")

        # 使用 PyAV 的 concat demuxer 读取所有分镜
        input_container = av.open(
            str(concat_list_path),
            options={"safe": "0", "an": "1"},
            format="concat",
        )
        input_stream = input_container.streams.video[0]

        # 创建输出容器，使用与输入相同的编码参数
        output_container = av.open(final_path, mode="w")
        output_stream = output_container.add_stream(
            input_stream.codec_context.name,
            rate=input_stream.average_rate,
        )
        output_stream.width = input_stream.codec_context.width
        output_stream.height = input_stream.codec_context.height
        output_stream.pix_fmt = input_stream.codec_context.pix_fmt

        # 解码所有帧并重新编码到输出（确保时间戳连续）
        for frame in input_container.decode(video=0):
            for packet in output_stream.encode(frame):
                output_container.mux(packet)

        # 刷新编码器缓冲
        for packet in output_stream.encode():
            output_container.mux(packet)

        output_container.close()
        input_container.close()

        # 清理临时文件
        os.remove(concat_list_path)

        if os.path.exists(final_path):
            return final_path

    except ImportError:
        print("⚠️ PyAV 未安装，尝试使用 CLI ffmpeg...")
    except Exception as e:
        print(f"⚠️ PyAV 合并失败: {e}，尝试使用 CLI ffmpeg...")

    # 方式2: 回退到 CLI ffmpeg
    ffmpeg_cmd = shutil.which("ffmpeg")
    if not ffmpeg_cmd:
        print("⚠️ ffmpeg 未找到，无法合并视频")
        return None

    concat_list_path = os.path.join(output_dir, "_concat_list.txt")
    try:
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for vp in video_paths:
                abs_path = os.path.abspath(vp).replace("\\", "/")
                f.write(f"file '{abs_path}'\n")

        cmd = [
            ffmpeg_cmd, "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            final_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(final_path):
            os.remove(concat_list_path)
            return final_path
        else:
            print(f"⚠️ ffmpeg 合并失败: {result.stderr[-300:] if result.stderr else '未知错误'}")
            return None
    except Exception as e:
        print(f"⚠️ 视频合并异常: {e}")
        return None


# 程序入口点：当脚本被直接运行时（而不是被导入），执行main函数
if __name__ == "__main__":
    # 调用主函数，开始执行程序逻辑
    main()
