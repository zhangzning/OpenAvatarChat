import sys

import gradio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from engine_utils.directory_info import DirectoryInfo
from service.service_utils.logger_utils import config_loggers
from service.service_utils.service_config_loader import load_configs
from service.service_utils.ssl_helpers import create_ssl_context

project_dir = DirectoryInfo.get_project_dir()
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)


import argparse
import os
from pathlib import Path

import gradio as gr

from chat_engine.chat_engine import ChatEngine
from fastapi.staticfiles import StaticFiles  # ✅ 引入静态文件支持
from fastapi.responses import FileResponse



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, help="service host address")
    parser.add_argument("--port", type=int, help="service host port")
    parser.add_argument("--config", type=str, default="config/chat_with_minicpm.yaml", help="config file to use")
    parser.add_argument("--env", type=str, default="default", help="environment to use in config file")
    return parser.parse_args()


def setup_demo():
    app = FastAPI()

    
    @app.get("/favicon.ico")
    async def favicon():
        print('--------------------------------------ddddddddddddddddd')
        return FileResponse(static_path / "favicon.ico")


    # ✅ 挂载 static 文件夹，用于 favicon.ico 等
    static_path = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_path), name="static")    
    print('----------------------------------------------------------------------------------------------------',static_path)
    @app.get("/")
    def get_root():
        return RedirectResponse(url="/ui")

    css = """


    .app {
        @media screen and (max-width: 768px) {
            padding: 8px !important;
        }
    }
    footer {
        display: none !important;
    }
    """
    with gr.Blocks(css=css, title="哈哈哈哈哈哈") as gradio_block:
        with gr.Column():
            with gr.Group() as rtc_container:
                pass
    gradio.mount_gradio_app(app, gradio_block, "/ui", app_kwargs={"favicon_path": "favicon.ico"})
    return app, gradio_block, rtc_container

def main():
    args = parse_args()
    logger_config, service_config, engine_config = load_configs(args)


    # 设置modelscope的默认下载地址
    if not os.path.isabs(engine_config.model_root):
        os.environ['MODELSCOPE_CACHE'] = os.path.join(DirectoryInfo.get_project_dir(),
                                                      engine_config.model_root.replace('models', ''))

    config_loggers(logger_config)
    chat_engine = ChatEngine()
    demo_app, ui, parent_block = setup_demo()

    chat_engine.initialize(engine_config, app=demo_app, ui=ui, parent_block=parent_block)

    ssl_context = create_ssl_context(args, service_config)
    uvicorn.run(demo_app, host=service_config.host, port=service_config.port, **ssl_context)


if __name__ == "__main__":
    main()
