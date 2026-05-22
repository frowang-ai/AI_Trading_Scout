from __future__ import annotations

from get_data_cls.run_cls_raw_reverse_loop import (
    DEFAULT_SLEEP_SECONDS,
    LOCK_PATH,
    LOOP_LOG_PATH,
    checkpoint_summary,
    run_loop,
)


def main() -> None:
    if DEFAULT_SLEEP_SECONDS != 1800:
        raise AssertionError(f"默认休息时间不是 1800 秒：{DEFAULT_SLEEP_SECONDS}")

    summary = checkpoint_summary(None)
    for field in ["completed", "last_time", "last_ctime", "total_pages", "total_rows"]:
        if field not in summary:
            raise AssertionError(f"checkpoint_summary 缺少字段：{field}")

    run_loop(max_runs=0)

    if not LOOP_LOG_PATH.parent.exists():
        raise AssertionError(f"日志目录未创建：{LOOP_LOG_PATH.parent}")
    if LOCK_PATH.exists():
        raise AssertionError(f"max_runs=0 不应创建锁文件：{LOCK_PATH}")

    print(f"loop log path: {LOOP_LOG_PATH}")
    print(f"lock path: {LOCK_PATH}")
    print("raw reverse loop diagnostic passed")


if __name__ == "__main__":
    main()
