
class EventEngine:
    """
    Presence:
    PRODUCT_APPEAR
    PRODUCT_DISAPPEAR
    PRODUCT_AT_SIDE
    PRODUCT_AT_FRONT
    PRODUCT_CARRIED
    PRODUCT_CARRIED_BY_BOTH_GLOVES
    GLOVE_LEFT_APPEAR
    GLOVE_LEFT_DISAPPEAR
    GLOVE_RIGHT_APPEAR
    GLOVE_RIGHT_DISAPPEAR
    """

    def __init__(self):
        self.events = set()

    def is_overlap(self, boxA, boxB):
        if boxA is None or boxB is None:
            return False

        return not (
            boxA.x2 < boxB.x1 or  # A 在 B 左邊
            boxA.x1 > boxB.x2 or  # A 在 B 右邊
            boxA.y2 < boxB.y1 or  # A 在 B 上面
            boxA.y1 > boxB.y2     # A 在 B 下面
        )

    # ======================================================
    # CORE UPDATE
    # ======================================================
    def update(self, obs):
        self.events.clear()

        product = obs['product']
        gl = obs['glove_left']
        gr = obs['glove_right']
        front = obs['front']
        side = obs['side']
        gl_box = gl.bbox if gl else None
        gr_box = gr.bbox if gr else None
        front_box = front.bbox if front else None
        side_box = side.bbox if side else None
        p_box  = product.bbox if product else None
        item_in_PLATFORM = obs['EFSevents']

        if product:
            self.events.add("PRODUCT_APPEAR")
        
        if (gl or gr) and (self.is_overlap((gl_box or gr_box), front_box)):
            self.events.add("GLOVE_AT_FRONT")
        if (gl or gr) and (self.is_overlap((gl_box or gr_box), side_box)):
            self.events.add("GLOVE_AT_SIDE")

        if product and (self.is_overlap(p_box, front_box)):
            self.events.add("PRODUCT_AT_FRONT")
        if product and (self.is_overlap(p_box, side_box)):
            self.events.add("PRODUCT_AT_SIDE")

        if product and (self.is_overlap(p_box, gl_box) or self.is_overlap(p_box, gr_box)):
            self.events.add("PRODUCT_CARRIED")
        if product and self.is_overlap(p_box, gl_box) and self.is_overlap(p_box, gr_box):
            self.events.add("PRODUCT_CARRIED_BY_BOTH_GLOVES")     

        if item_in_PLATFORM:
            for e in item_in_PLATFORM:
                if e["label"] == "glove":
                    self.events.add("GLOVE_IN_PLATFORM")
                if e["label"] == "product":
                    self.events.add("PRODUCT_IN_PLATFORM")

        # # DEBUG
        # print("OBSERVATION:", obs)
        # print("DEDUCED EVENTS:", self.events)   

        return self.events
