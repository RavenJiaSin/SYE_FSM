import cv2
import numpy as np
import json


# ==========================================
# 請設定你要讀取的影片路徑 (跟 config.py 一樣)
# ==========================================
VIDEO_SRC = r"D:\NCU\intern\workspace\EFS\program_example\sye_0414.mp4" 

# 全域變數
points = []
img_copy = None

def click_event(event, x, y, flags, param):
    global points, img_copy
    
    # 滑鼠左鍵點擊：新增頂點
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        cv2.circle(img_copy, (x, y), 5, (0, 0, 255), -1)
        
        # 畫出多邊形連線
        if len(points) >= 2:
            cv2.line(img_copy, tuple(points[-2]), tuple(points[-1]), (0, 255, 0), 2)
        
        cv2.imshow("ROI Selector", img_copy)
        
    # 滑鼠右鍵點擊：清除所有點
    elif event == cv2.EVENT_RBUTTONDOWN:
        points = []
        img_copy = param.copy() # 還原成乾淨的圖片
        cv2.imshow("ROI Selector", img_copy)

def main():
    global img_copy
    
    print("正在開啟影片...")
    cap = cv2.VideoCapture(VIDEO_SRC)
    
    if not cap.isOpened():
        print("❌ 無法開啟影片！請檢查路徑。")
        return
        
    # 讀取影片解析度的標準函式
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"ℹ️ 原始影片解析度: {video_width} x {video_height}")
        
    ret, frame = cap.read()
    if not ret:
        print("❌ 無法讀取影片的第一幀。")
        cap.release()
        return

    # 另一種獲取解析度的方式 (從 frame 取得)，這裡用來作為計算比例的基準
    h, w = frame.shape[:2]

    # 如果影片太大，可以縮放視窗 (不影響 cv2 抓取原始圖片的座標)
    cv2.namedWindow("ROI Selector", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ROI Selector", 1280, 720)
        
    img_copy = frame.copy()
    cv2.imshow("ROI Selector", img_copy)
    
    # 綁定滑鼠事件
    cv2.setMouseCallback("ROI Selector", click_event, frame)
    
    print("\n" + "="*40)
    print("【使用說明】")
    print("1. 滑鼠左鍵：點擊新增多邊形頂點。")
    print("2. 滑鼠右鍵：清除所有點，重新開始。")
    print("3. 按下 'Enter' 鍵：完成選擇，印出「相對座標」並退出。")
    print("4. 按下 'q' 鍵：直接退出。")
    print("="*40 + "\n")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13: # Enter 鍵
            if len(points) >= 3:
                # 幫你把點連回起點，視覺上比較完整
                cv2.line(img_copy, tuple(points[-1]), tuple(points[0]), (0, 255, 0), 2)
                cv2.imshow("ROI Selector", img_copy)
                cv2.waitKey(500) # 顯示半秒鐘
                
                # === 核心修改：將絕對像素座標轉換為 0.0~1.0 的相對比例 ===
                normalized_points = []
                for p in points:
                    norm_x = round(p[0] / w, 4) # 保留小數點後四位
                    norm_y = round(p[1] / h, 4)
                    normalized_points.append({"x": norm_x, "y": norm_y})
                
                print("\n✅ 完成！請複製以下「相對座標」到 config.py：")
                print("ROI_COORDS_NORMALIZED =", json.dumps(normalized_points))
                break
            else:
                print("⚠️ 多邊形至少需要 3 個點！")
                
        elif key == ord('q'):
            print("已取消。")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
