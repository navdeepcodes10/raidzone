import os
import sys
import subprocess
import random
import math
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

def create_video():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    video_dir = "/Users/navdeep/raidzone-website/video"
    output_mp4 = "/Users/navdeep/Desktop/RaidZone_Launch_Video.mp4"
    
    # Load 4 scene images (1080 x 1920)
    print("Loading scene images...")
    s1 = Image.open(f"{video_dir}/scene1.png").convert("RGBA")
    s2 = Image.open(f"{video_dir}/scene2.png").convert("RGBA")
    s3 = Image.open(f"{video_dir}/scene3.png").convert("RGBA")
    s4 = Image.open(f"{video_dir}/scene4.png").convert("RGBA")
    
    W, H = 1080, 1920
    FPS = 30
    TOTAL_FRAMES = 480  # 16.0 seconds
    
    # Initialize 75 floating golden embers/particles
    random.seed(42)
    particles = []
    for _ in range(75):
        particles.append({
            'x': random.uniform(0, W),
            'y': random.uniform(0, H),
            'vx': random.uniform(-0.6, 0.6),
            'vy': random.uniform(-2.2, -0.8), # drifting upwards
            'size': random.uniform(2.5, 6.0),
            'brightness': random.uniform(0.4, 0.95),
            'pulse_speed': random.uniform(0.04, 0.08)
        })
        
    # Helper to apply slow cinematic camera push-in (zoom)
    def get_zoomed_frame(img, zoom_factor):
        # crop around center
        crop_w = int(W / zoom_factor)
        crop_h = int(H / zoom_factor)
        left = (W - crop_w) // 2
        top = (H - crop_h) // 2
        cropped = img.crop((left, top, left + crop_w, top + crop_h))
        return cropped.resize((W, H), Image.Resampling.BILINEAR)

    # Launch FFmpeg process piping raw frames
    cmd = [
        ffmpeg_exe,
        '-y',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgba',
        '-s', f'{W}x{H}',
        '-r', str(FPS),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-crf', '18',
        output_mp4
    ]
    
    print(f"Launching FFmpeg: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    # Timeline definitions (frame ranges and transitions)
    # Scene 1: 0 to 120 (transition 1->2 at 105..120)
    # Scene 2: 105 to 240 (transition 2->3 at 225..240)
    # Scene 3: 225 to 360 (transition 3->4 at 345..360)
    # Scene 4: 345 to 480 (fade to black at 465..480)
    
    print(f"Rendering {TOTAL_FRAMES} cinematic frames...")
    
    for f in range(TOTAL_FRAMES):
        # Determine active scene & transitions
        if f < 105:
            # Scene 1 pure
            t = f / 120.0
            zoom = 1.0 + 0.06 * t
            frame = get_zoomed_frame(s1, zoom)
        elif f < 120:
            # Blend Scene 1 and Scene 2
            alpha = (f - 105) / 15.0
            z1 = 1.0 + 0.06 * (f / 120.0)
            z2 = 1.0 + 0.05 * ((f - 105) / 135.0)
            f1 = get_zoomed_frame(s1, z1)
            f2 = get_zoomed_frame(s2, z2)
            frame = Image.blend(f1, f2, alpha)
        elif f < 225:
            # Scene 2 pure
            t = (f - 105) / 135.0
            zoom = 1.0 + 0.05 * t
            frame = get_zoomed_frame(s2, zoom)
        elif f < 240:
            # Blend Scene 2 and Scene 3
            alpha = (f - 225) / 15.0
            z2 = 1.0 + 0.05 * ((f - 105) / 135.0)
            z3 = 1.0 + 0.06 * ((f - 225) / 135.0)
            f2 = get_zoomed_frame(s2, z2)
            f3 = get_zoomed_frame(s3, z3)
            frame = Image.blend(f2, f3, alpha)
        elif f < 345:
            # Scene 3 pure
            t = (f - 225) / 135.0
            zoom = 1.0 + 0.06 * t
            frame = get_zoomed_frame(s3, zoom)
        elif f < 360:
            # Blend Scene 3 and Scene 4
            alpha = (f - 345) / 15.0
            z3 = 1.0 + 0.06 * ((f - 225) / 135.0)
            z4 = 1.0 + 0.07 * ((f - 345) / 135.0)
            f3 = get_zoomed_frame(s3, z3)
            f4 = get_zoomed_frame(s4, z4)
            frame = Image.blend(f3, f4, alpha)
        else:
            # Scene 4 pure (with final fade to black at end)
            t = (f - 345) / 135.0
            zoom = 1.0 + 0.07 * t
            frame = get_zoomed_frame(s4, zoom)
            if f >= 465:
                # Fade out to black over last 15 frames
                fade_alpha = (f - 465) / 15.0
                black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
                frame = Image.blend(frame, black, fade_alpha)

        # Draw cinematic golden floating embers
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for p in particles:
            # update position
            p['x'] = (p['x'] + p['vx']) % W
            p['y'] = (p['y'] + p['vy']) % H
            # pulsating alpha
            pulse = (math.sin(f * p['pulse_speed']) + 1.0) / 2.0
            current_brightness = int(255 * p['brightness'] * (0.6 + 0.4 * pulse))
            rad = p['size']
            # Gold color: rgba(255, 205, 60, alpha)
            draw.ellipse(
                [p['x'] - rad, p['y'] - rad, p['x'] + rad, p['y'] + rad],
                fill=(255, 205, 60, current_brightness)
            )
            # Subtle outer glow halo for larger embers
            if rad > 3.5:
                draw.ellipse(
                    [p['x'] - rad*2, p['y'] - rad*2, p['x'] + rad*2, p['y'] + rad*2],
                    fill=(255, 180, 40, int(current_brightness * 0.3))
                )

        # Composite embers on top of frame
        final_frame = Image.alpha_composite(frame, overlay)
        
        # Pipe frame bytes to FFmpeg
        proc.stdin.write(final_frame.tobytes())
        
        if f % 60 == 0 or f == TOTAL_FRAMES - 1:
            print(f"Rendered frame {f+1}/{TOTAL_FRAMES} ({(f+1)/TOTAL_FRAMES*100:.1f}%)")

    proc.stdin.close()
    proc.wait()
    print(f"Video rendering complete! File saved to: {output_mp4}")

if __name__ == "__main__":
    create_video()
