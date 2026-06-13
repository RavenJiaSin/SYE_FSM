class Logger:

    @staticmethod
    def warn(msg, direction=None):
        print(f"[WARNING] [{direction}] {msg}")

    @staticmethod
    def info(msg, direction=None):
        print(f"[INFO___] [{direction}] {msg}")

    @staticmethod
    def fsm_info(msg, direction=None):
        # print(f"[FSMINFO] [{direction}] {msg} ===")
        pass
