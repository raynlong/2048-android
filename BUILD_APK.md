# 如何构建 2048 APK

## 方法一：Android Studio（推荐，最简单）

1. 下载安装 [Android Studio](https://developer.android.com/studio)
2. 打开 Android Studio → **Open** → 选择本文件夹（`android/`）
3. 等待 Gradle 同步（首次需下载依赖，约 5-10 分钟）
4. 菜单：**Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
5. 构建完成后点提示中的 **locate** 找到 APK 文件
   - 路径：`app/build/outputs/apk/debug/app-debug.apk`

## 方法二：命令行（需要已配置 ANDROID_HOME）

```bash
cd android
./gradlew assembleDebug
# APK 位于: app/build/outputs/apk/debug/app-debug.apk
```

## 注意事项

- 需要 JDK 17+（已在本机安装：Microsoft OpenJDK 17）
- 首次构建需要联网下载 Gradle 和 Android 依赖
- Debug APK 可直接安装到手机（需在手机开启"允许未知来源"）

## 项目结构说明

```
android/
├── app/
│   ├── build.gradle          # 应用构建配置
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── assets/           # ← 游戏 Web 文件（index.html、js、style）
│       ├── java/com/game/app2048/
│       │   └── MainActivity.java  # ← WebView 容器
│       └── res/
│           ├── layout/activity_main.xml
│           ├── mipmap-*/ic_launcher.png  # 图标
│           └── values/
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## 游戏汉化说明

已修改的文字：
- "Join the numbers..." → "合并数字，达到 2048！"
- "New Game" → "新游戏"
- "Keep going" → "继续游戏"
- "Try again" → "再来一局"
- "You win!" → "恭喜获胜！"
- "Game over!" → "游戏结束！"
- "Score" → "得分"
- "Best" → "最高"
- "How to play" → "玩法说明"
