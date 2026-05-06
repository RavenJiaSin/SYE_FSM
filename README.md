# SYE FSM

王嘉信

## 一、專案情境

生益電子的產品搬運。

### 正確流程：

操作員將產品從架上取下

以雙手將產品搬運至裝載台

將產品放置於裝載台並手離開裝載台

### Case 1.

搬運產品時應以雙手搬運，否則應紀錄警告

### Case 2.

將產品放置於裝載台的動作應該一次完成
放置後手不應該再次進入裝載台，否則應紀錄警告

本專案將呼叫 LEDA_APP 的物件偵測與電子圍籬[API](http://leda-app.seadeep.ai/openapi/swagger)作為視覺偵測，並使用python 撰寫 一有限狀態機來實作以上情境偵測

## 二、專案架構

```
📦SYE_FSM
 ┣ 📂fsm
 ┃ ┣ 📜base_state.py
 ┃ ┣ 📜carry_state.py
 ┃ ┣ 📜context.py
 ┃ ┣ 📜idle_state.py
 ┃ ┣ 📜place_state.py
 ┃ ┣ 📜state_registry.py
 ┃ ┗ 📜wait_place_state.py
 ┣ 📂template_cam
 ┃ ┗ 📜sye_special.mp4
 ┣ 📂utils
 ┃ ┗ 📜logger.py
 ┣ 📂vision
 ┃ ┣ 📜camera_client.py
 ┃ ┣ 📜efs_client.py
 ┃ ┣ 📜event_engine.py
 ┃ ┣ 📜od_client.py
 ┃ ┣ 📜perception.py
 ┃ ┣ 📜types.py
 ┃ ┗ 📜vision_system.py
 ┣ 📜config.py
 ┗ 📜main.py
```

### (一)物件偵測模型

在開始設計前須先釐清模型能偵測畫面中那些物件

>記得將權重檔案放到 `LEDA-APP\earth-api\weights\od\sye`

OD
1. 產品 `product`
2. 操作員的手(手套) `glove`
3. 操作員 `operator` **未使用*
4. 貨架 `side` **未使用*

EFS

能偵測指定範圍 `PLATFORM` 中出現的OD物件及其個數

### (二)📂有限狀態機 fsm

![image](https://hackmd.io/_uploads/HJ0cGHkCWe.png)

如此設計FSM能解決Case 1.與 Case 2.和以下幾種特殊情況：

1. 環境中偵測到 `product` 但並沒有搬運
2. `product` 於搬運過程中遺失
3. `product` 於搬運過程中經過 `PLATFORM` 但未放置

#### 📜BaseState *`base_state.py`*

定義了"狀態(state)"物件的抽象類別(abstract class)，
每個state都要實作抽象方法(abstract methods):

```python
update(self, events)
# events:用來觸發狀態轉移的事件
```

>BaseState 是 State 的 "藍圖"，其他 State 要繼承 BaseState
>
>由於 Python 語法沒有直接支援抽象類別，所以要
>
>```python
>from abc import ABC, abstractmethod
>```

#### 📜STATE_MAP *`state_registry`*

要了解為何需要這個檔案，我們可以看以下範例:

>假如有以下狀態轉換
>
>```
>State_A --> State_B
>State_B --> State_A
>```
>
>`state_a.py` 要 
>
>```python 
>from state_b import State_B
>```
>
>`state_b.py` 要 
>
>```python 
>from state_a import State_A
>```
>
>會造成 circular import error
>
>因為Python 載入模組是「執行檔案」，
當執行 A 的初始化時發現要 import B，於是執行 B，發現 B 的初始化要 import A，於是執行 A，發現A 的初始化要...循環...爆炸

為了不要發生circular import，這邊讓所有 state 只依賴 FSMcontext，FSMcontext 再透過 STATE_MAP 用名稱查表找 class

```
IdleState ─┐
CarryState ├──→ STATE_MAP ←── FSMContext
WaitPlace ─┘
```

```python
STATE_MAP = {
    "idle": IdleState,
    "carry": CarryState,
    "wait_place": WaitPlaceState,
    "place": PlaceState,
}
```

#### 📜FSMContext *`context.py`*

狀態控制器，負責處理持有「當前狀態」以及 控制「狀態轉移」

初始化 state（用字串 → class mapping）
```python
self.state = STATE_MAP[initial_state_name](self)
```
切換狀態（重新建立 state instance）
```python
def transition_to(self, state_name):
```
將事件交給「目前狀態」處理
```python
def update(self, events):
    self.state.update(events)
```
#### 📜FSM 執行流程（Runtime Flow）

```python
# main.py
fsm = FSMContext('idle') # 初始為 idle_State
...
fsm.update(events) # 每一 frame 更新狀態
    
# FSMContext.update()
#     ↓
# current_state.update(events)
#     ↓
# (可能呼叫)
# context.transition_to(new_state)
```
#### 📜IdleState *`idle_state.py`*
```python
if "PRODUCT_APPEAR" in events and "PRODUCT_CARRIED" in events:
    → carry_state
```
>條件：product 出現 且 被拿起
> → 切換成CarryState

```python
if "GLOVE_IN_PLATFORM" in events:
    Logger.warn("手中沒product不應該觸碰PLATFORM")
```
>idle時 手不應該碰平台 → warning

#### 📜CarryState *`carry_state.py`*
* product 消失檢查
    ```python
    if 'PRODUCT_APPEAR' not in events:
    ```
    累計 `self.missing_product_frames += 1`
    若超過閾值則 
    ```python
    if self.missing_product_frames > self.context.N_MISSING_FRAMES:
                Logger.warn("product 於搬運中消失")
                self.context.transition_to("idle")
    ```
    >為何要累計消失frame? >> 避免 detection noise
* 雙手搬運檢查
    ```python
    if 'PRODUCT_CARRIED_BY_BOTH_GLOVES' not in events:
            self.no_double_hand_frames += 1
            if self.no_double_hand_frames > self.context.N_DOUBLE_HAND_FRAMES:
                Logger.warn("未使用雙手搬運")
    ```

* 進入裝載台
    ```python
    if 'PRODUCT_IN_PLATFORM' in events:
        → wait_place_state
    ```

#### 📜WaitPlaceState *`wait_place_state.py`*

為何不直接進入 PlaceState ?

因為搬運過程中 product 可能只是"擦過" PLATFORM ，並沒有放置

```python
if PRODUCT_APPEAR not in events:
    # product 消失（表示放下）
    → place_state
```
```python
if timeout_frame_counter > WAIT_TIMEOUT_FRAMES:
    # 太久沒放好
    → carry_state
```

#### 📜PlaceState *`place_state.py`*

```python
if 'GLOVE_IN_PLATFORM' not in events:
    # 手離開平台 → 完成
    → idle_state
```

```python
if place_frames > MIN_PLACE_FRAMES:
    # 手不能在裝載台中一直亂摸停留
    → idle_state
    # idle_state 時會對手進入裝載台提出警告
```


### (三)📂視覺模組 vision
呼叫 LEDA_APP 的 API，辨識畫面中的物件，並將辨識結果轉成 events 輸入 FSM
```
Camera → (OD / EFS API)
           ↓
     Client Layer（HTTP）
           ↓
     Perception（解析）
           ↓
     VisionSystem（整合）
           ↓
     EventEngine（事件抽象）
           ↓
          FSM
```

#### 📜CameraClient *`camera_client.py`*
負責設定以及開關API camera
```python
def open(self, name, src):
             # 相機名稱, 影像來源(影片路徑或鏡頭)
```
```python
def close(self, name):
```

#### 📜ODClient *`od_client.py`*
負責Oject Detection API的呼叫
```python
def __init__(self, url: str,camera_name: str, task_name: str, model_name: str, threshold: float):
```
```python
def infer_live(self):
        resp = self.session.get(
            f"{self.url}/api/infer_od/live_result",
            params={"name": self.task_name},
        ).json()

        if resp.get("code") != 0:
            return None

        return resp.get("result")
```
> 回傳格式可以參考[API文件](http://leda-app.seadeep.ai/openapi/swagger#/Object%20Detection/infer_v8_od_live_result_api_infer_od_live_result_get)
> 或 執行 `📜test_od_API.py` 觀察

#### 📜EFSClient *`efs_client.py`*
負責Electronic Fence System API的呼叫
(模型偵測來源中"特定範圍"中出現的物件及其位置)

```python
def __init__(self, url: str, camera_name: str, task_name: str, model_name: str, alert_area: dict, threshold: float):
# 注意 alert_area的格式是list[dict]
# [
#     {"x": 0.6289, "y": 0.7625},
#     {"x": 0.5266, "y": 0.7917},
#     ...
#     {"x": 0.3891, "y": 0.9931},
# ]
```
```python
def infer_live(self):
        resp = self.session.get(
            f"{self.url}/api/infer_efs/live_result",
            params={"name": self.task_name},
        ).json()

        if resp.get("code") != 0:
            return None

        return resp.get("result")
```
> 回傳格式可以參考[API文件](http://leda-app.seadeep.ai/openapi/swagger#/Electronic%20Fence%20System/infer_efs_live_result_api_infer_efs_live_result_get)
> 或 執行 `📜test_efs_API.py` 觀察

#### 📜資料結構 *`types.py`*
Bounding Box：x1, y1, x2, y2

封裝偵測結果：

* 類別（product / glove）
* 信心值（confidence）
* bbox

#### 📜Perception *`perception.py`*
`raw data → structured data`

處理由 od 和 efs 獲得的資料，將兩者合併成一份偵測結果
```python
def merge(self, od, efs):
        od_p = self.parse_od(od)
        efs_p = self.parse_efs(efs)

        return {
            # object-level perception
            "product": od_p["product"],
            "glove_left": od_p["glove_left"],
            "glove_right": od_p["glove_right"],
            # raw event stream (NO interpretation)
            "EFSevents": efs_p,
        }
```

#### 📜VisionSystem *`vision_system.py`*
呼叫 OD API 與 EFS API，將偵測結果丟給 perception
再回傳 observation

#### 📜EventEngine *`event_engine.py`*
將偵測結果進行邏輯判斷，並轉換成事件(events)
1. 產品出現
```python
if product:
    → "PRODUCT_APPEAR"
```
2. 產品搬運
```python
if overlap(product, glove_left) or overlap(product, glove_r):
    → "PRODUCT_CARRIED"
```
```python
if overlap(product, glove_left) and overlap(product, glove_r):
    → "PRODUCT_CARRIED_BY_BOTH_GLOVES"
```
3. 平台事件（EFS）
```python
if e["label"] == "glove":
    → "GLOVE_IN_PLATFORM"
```
```python
if e["label"] == "product":
    → "PRODUCT_IN_PLATFORM"
```

最終回傳一個 events se

### 主程式 *`main.py`*

調用 `config.py` 的參數，並開啟live連結

```python
def main():

    # ================= INIT =================
    camera = CameraClient(cfg.URL)
    od = ODClient(cfg.URL, cfg.CAM_NAME, cfg.TASK_NAME, cfg.MODEL_NAME, cfg.THRESHOLD)
    efs = EFSClient(cfg.URL, cfg.CAM_NAME, cfg.TASK_NAME, cfg.MODEL_NAME, cfg.ALERT_AREA, cfg.THRESHOLD)

    perception = Perception()
    vision = VisionSystem(od, efs, perception)
    event = EventEngine()

    fsm = FSMContext('idle')

    # bind config to FSM
    fsm.N_MISSING_FRAMES = cfg.N_MISSING_FRAMES
    fsm.N_DOUBLE_HAND_FRAMES = cfg.N_DOUBLE_HAND_FRAMES
    fsm.WAIT_TIMEOUT_FRAMES = cfg.WAIT_TIMEOUT_FRAMES
    fsm.MIN_PLACE_FRAMES = cfg.MIN_PLACE_FRAMES

    # ================= START =================
    camera.open(cfg.CAM_NAME, cfg.CAM_SRC)
    od.init_model()
    efs.init_model()

    od.start()
    efs.start()

    print("SYSTEM STARTED")

    stream_url = f"{cfg.URL}/api/infer_od/live?name={cfg.TASK_NAME}"
    webbrowser.open(stream_url)

    # ================= LOOP =================
    try:
        while True:
            # 1. get fused observation
            obs = vision.step()

            # 2. event engine
            events = event.update(obs)

            # 3. update FSM
            fsm.update(events)

            # 4. debug output (optional)
            # print(f"Events: {events}")

            time.sleep(0.03)  # ~30 FPS control

    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT - STOPPING SYSTEM")
    except Exception as e:
        print(e)
        print("STOPPING SYSTEM")

    finally:
        od.stop()
        efs.stop()
        camera.close(cfg.CAM_NAME)
```

## 三、操作教學
1. 修改 `config.py` 中 `CAM_SRC` 路徑 以及 `ALERT_AREA` (PLATFORM區域)
2. 將權重檔案放到 `LEDA-APP\earth-api\weights\od\sye`
3. 啟用LEDA_APP `python app.py`
4. 開另一個終端機 啟用syeFSM `python main.py`
5. 按下`Ctrl`+`C`終止
