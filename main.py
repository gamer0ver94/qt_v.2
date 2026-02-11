from core.qt_core import App
from modules import (
    DashboardModule,
    SystemStatusModule,
    CPUWidget,
    MemoryWidget,
    DiskWidget,
    LogModule,
    GitManagerModule
)


def main():
    app = App(single=True)

    app.register_module(
        [
            # New Dashboard - User Session Display (uses system user)
            # Left: User info (from system), Middle: Image (optional),
            # Right: Time info (from system login time)
            DashboardModule(
                app,
                user_image=None,  # Pass an image path or PIL Image here
                bg_color="#ffffff",
                fg_color="#000000"
            ),
            # System Status - CPU, Memory, Disk widgets
            SystemStatusModule(
                app,
                widgets=[
                    CPUWidget,
                    MemoryWidget,
                    DiskWidget,
                ],
                bg_color="#ffffff",
                fg_color="#000000"
            ),
            LogModule(app, log_file="main.py", fg_color="white"),
            GitManagerModule(app)
        ]
    )

    app.run()


if __name__ == "__main__":
    main()

