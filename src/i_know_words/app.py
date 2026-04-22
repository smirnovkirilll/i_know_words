#!/usr/bin/env python3

import argparse
import json
import math
import os
import random
import rumps
import subprocess
import webbrowser
import yaml
from collections import deque
from importlib import resources
from pathlib import Path


APP_NAME = "i_know_words"
CONFIG_YAML = "config.yaml"
DEFAULT_INTERVAL = 10
DEFAULT_HISTORY_LENGTH = 10


def get_default_config_path():
    try:
        return resources.files(APP_NAME).joinpath(CONFIG_YAML)
    except:
        return CONFIG_YAML


class DictionaryModel:
    def __init__(self, name, path, config, history_length):
        self.name = name
        self.path = path
        self.config = config
        self.words = self.load()
        self.weights = self.prepare_weights()
        self.current = None
        self.history_length = history_length
        self.history = deque(maxlen=history_length)

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def prepare_weights(self):
        ranking = self.config.get("ranking", {})

        if not ranking.get("enabled"):
            return None

        key = ranking["key"]
        weights = []

        for w in self.words:
            rank = w.get(key, 10000)

            try:
                rank = float(rank)
                weights.append(1.0 / math.log(rank + 1))
            except:
                weights.append(0.0001)

        return weights

    def pick(self):
        if not self.weights:
            candidate = random.choice(self.words)
        else:
            candidate = random.choices(self.words, weights=self.weights, k=1)[0]

        # anti-repeat
        if self.current and len(self.words) > 1:
            for _ in range(5):
                if candidate != self.current:
                    break
                candidate = random.choice(self.words)

        self.current = candidate
        self.history.appendleft(candidate)
        return candidate


class MenuRenderer:
    def __init__(self, app):
        self.app = app

    @staticmethod
    def append_div_line(menu):
        menu.append(None)

    def build(self):
        model = self.app.current_model
        cfg = model.config

        menu = []

        # --- DICTIONARIES ---
        for name in self.app.models:
            title = f"✓ {name}" if name == self.app.current_name else name

            menu.append(
                rumps.MenuItem(title, callback=self.app.switch_dict)
            )
        self.append_div_line(menu)

        word = model.current or {}
        word_key = cfg["menu_items"]["word"]
        tr_key = cfg["menu_items"]["translation"]
        show_tr_in_bar = cfg.get("show_translation_in_bar", False)

        # --- DYNAMIC ITEMS ---
        for label, key in cfg["menu_items"].items():
            value = word.get(key, "")

            # --- filters ---
            if key == word_key:
                continue
            if key == tr_key and show_tr_in_bar:
                continue
            if not value:
                continue

            value_str = str(value)

            # --- LONG TEXT → submenu (hover-like UX) ---
            if len(value_str) > 40:
                parent = rumps.MenuItem(f"{label}: {value_str[:40]}...")

                parent.add(
                    rumps.MenuItem(
                        value_str,
                        callback=lambda _, v=value_str: self.app.copy_to_clipboard(v)
                    )
                )
                item = parent

            # --- LINK ---
            elif isinstance(value, str) and value.startswith("https://"):
                item = rumps.MenuItem(
                    label,
                    callback=lambda _, url=value: self.app.open_url(url)
                )

            # --- NORMAL ---
            else:
                item = rumps.MenuItem(
                    f"{label}: {value_str} ⧉",
                    callback=lambda _, v=value_str: self.app.copy_to_clipboard(v)
                )

            menu.append(item)

        # --- HISTORY ---
        if model.history:
            self.append_div_line(menu)
            history_menu = rumps.MenuItem("History")

            for w in list(model.history)[:model.history_length]:
                text = str(w.get(word_key, ""))

                history_menu.add(
                    rumps.MenuItem(
                        text,
                        callback=lambda _, v=text: self.app.copy_to_clipboard(v)
                    )
                )

            menu.append(history_menu)

        # --- NEXT ---
        menu.append(
            rumps.MenuItem(
                "Next",
                callback=lambda _: self.app.next_word()
            )
        )

        # --- FOOTER ---
        self.append_div_line(menu)
        if self.app.footer:
            label = self.app.footer["label"]
            url = self.app.footer["url"]
            menu.append(
                rumps.MenuItem(
                    label,
                    callback=lambda _, url=url: self.app.open_url(url)
                )
            )
        menu.append(
            rumps.MenuItem(
                "Quit",
                callback=lambda _: rumps.quit_application()
            )
        )

        return menu


class WordApp(rumps.App):
    def __init__(self, config_path):
        super().__init__("Word")

        self.config_path = config_path
        self.config_dir = os.path.dirname(os.path.abspath(config_path))
        self.config = self.load_config(config_path)
        self.history_length = self.config.get("history_length", DEFAULT_HISTORY_LENGTH)
        self.interval = self.get_interval()
        self.timer = None
        self.footer = self.config.get("footer")

        self.models = {}
        for name, cfg in self.config["dictionaries"].items():
            key = self.normalize_name(name)
            model_cfg = self.config["display"][key]
            path = cfg if isinstance(cfg, str) else cfg["path"]
            resolved_path = Path(self.resolve_path(path))
            self.models[name] = DictionaryModel(name, resolved_path, model_cfg, self.history_length)

        self.current_name = self.config["default"]
        self.current_model = self.models[self.current_name]

        self.renderer = MenuRenderer(self)
        self.start_timer()
        self.update_word(None)

    def resolve_path(self, path_str):
        p = Path(path_str)
        if p.is_absolute():
            return p

        candidate = Path(self.config_dir) / p
        if candidate.exists():
            return candidate

        try:
            return resources.files(APP_NAME).joinpath(path_str)
        except:
            pass

        return p

    @staticmethod
    def normalize_name(name):
        return name.lower().replace(" ", "_").replace("→", "_").replace("-", "_")

    @staticmethod
    def load_config(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def get_interval(self):
        if self.config.get("timer") and self.config["timer"].get("enabled", False):
            return self.config["timer"].get("interval", DEFAULT_INTERVAL)
        return None

    def start_timer(self):
        if self.interval:
            self.timer = rumps.Timer(self.update_word, self.interval)
            self.timer.start()

    @staticmethod
    def copy_to_clipboard(text):
        subprocess.run("pbcopy", text=True, input=str(text))

    @staticmethod
    def open_url(url):
        webbrowser.open(url)

    def next_word(self):
        self.update_word(None)

    def update_word(self, _):
        word = self.current_model.pick()
        cfg = self.current_model.config
        word_key = cfg["menu_items"]["word"]
        tr_key = cfg["menu_items"]["translation"]

        if cfg.get("show_translation_in_bar"):
            self.title = f"{word.get(word_key, '')} - {word.get(tr_key, '')}"
        else:
            self.title = word.get(word_key, "")

        self.rebuild_menu()

    def switch_dict(self, sender):
        name = sender.title.replace("✓ ", "")

        self.current_name = name
        self.current_model = self.models[name]

        self.update_word(None)

    def rebuild_menu(self):
        menu = self.renderer.build()

        self.menu.clear()
        for item in menu:
            self.menu.add(item)

    @rumps.clicked("Word")
    def on_click(self, _):
        self.rebuild_menu()


def main():
    parser = argparse.ArgumentParser(
        description="A minimalistic menubar app designed for people who obviously don't know all the words yet (rumps + yaml)"
    )
    parser.add_argument(
        "--config_path",
        help="Path to external config.yaml (optional)",
    )
    args = parser.parse_args()
    config_path = args.config_path or get_default_config_path()
    WordApp(config_path).run()


if __name__ == "__main__":
    main()
