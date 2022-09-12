from __future__ import annotations

import logging
import os
import pickle
from datetime import timedelta
from hashlib import md5

import requests
from homeassistant.components.camera import Camera
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_PHOTOS_ENTITY,
    CONF_PHOTOS,
    CONF_IMG_UPDATE_EVENT,
    CONF_IMG_UPDATE_INTERVAL_SECONDS,
    CONF_IMG_UPDATE_INTERVAL_SECONDS_DEFAULT,
    CONF_MAX_NB_IMAGES,
    CONFIG_URL_DUMP_FILENAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up the Camera that displays images from Strava.
    Works via image-URLs, not via local file storage
    """

    if not config_entry.data.get(CONF_PHOTOS, False):
        camera = UrlCam(default_enabled=False)
    else:
        camera = UrlCam(default_enabled=True)

    async_add_entities([camera])

    def image_update_listener(now):
        if len(ha_strava_config_entries) != 1:
            return -1

        camera.rotate_img()

    ha_strava_config_entries = hass.config_entries.async_entries(domain=DOMAIN)
    img_update_interval_seconds = int(
        ha_strava_config_entries[0].options.get(
            CONF_IMG_UPDATE_INTERVAL_SECONDS,
            CONF_IMG_UPDATE_INTERVAL_SECONDS_DEFAULT,
        )
    )

    async_track_time_interval(hass, image_update_listener, timedelta(seconds=img_update_interval_seconds))

    return


class UrlCam(Camera):
    """
    Representation of a camera entity that can display images from Strava Image URL.
    Image URLs are fetched from the strava API and the URLs come as payload of the strava data update event
    Up to 100 URLs are stored in the Camera object
    """

    def __init__(self, default_enabled=True):
        """Initialize Camera component."""
        super().__init__()

        self._url_dump_filepath = os.path.join(
            os.path.split(os.path.abspath(__file__))[0], CONFIG_URL_DUMP_FILENAME
        )
        _LOGGER.debug(f"url dump filepath: {self._url_dump_filepath}")

        if os.path.exists(self._url_dump_filepath):
            with open(self._url_dump_filepath, "rb") as file:
                self._urls = pickle.load(file)
        else:
            self._urls = {}
            self._pickle_urls()

        self._url_index = 0
        self._default_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/No_image_available_600_x_450.svg/1280px-No_image_available_600_x_450.svg.png"
        self._max_images = CONF_MAX_NB_IMAGES
        self._default_enabled = default_enabled

    def _pickle_urls(self):
        """store image urls persistently on hard drive"""
        with open(self._url_dump_filepath, "wb") as file:
            pickle.dump(self._urls, file)

    def _return_default_img(self):
        img_response = requests.get(url=self._default_url)
        return img_response.content

    def is_url_valid(self, url):
        """test whether an image URL returns a valid response"""
        img_response = requests.get(url=url)
        if img_response.status_code == 200:
            return True
        _LOGGER.error(
            f"{url} did not return a valid image | Response: {img_response.status_code}"
        )
        return False

    def camera_image(
            self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return image response."""
        if len(self._urls) == self._url_index:
            _LOGGER.debug("No custom image urls....serving default image")
            return self._return_default_img()

        img_response = requests.get(
            url=self._urls[list(self._urls.keys())[self._url_index]]["url"]
        )
        if img_response.status_code == 200:
            return img_response.content
        else:
            _LOGGER.error(
                f"{self._urls[list(self._urls.keys())[self._url_index]]['url']} did not return a valid image. Response: {img_response.status_code}"
            )
            return self._return_default_img()

    def rotate_img(self):
        _LOGGER.debug(f"Number of images available from Strava: {len(self._urls)}")
        if len(self._urls) == 0:
            return
        self._url_index = (self._url_index + 1) % len(self._urls)
        self.async_write_ha_state()
        return
        # self.schedule_update_ha_state()

    @property
    def state(self):
        if len(self._urls) == self._url_index:
            return self._default_url
        return self._urls[list(self._urls.keys())[self._url_index]]["url"]

    @property
    def unique_id(self):
        return CONF_PHOTOS_ENTITY

    @property
    def name(self):
        """Return the name of this camera."""
        return CONF_PHOTOS_ENTITY

    @property
    def should_poll(self):
        return False

    @property
    def extra_state_attributes(self):
        """Return the camera state attributes."""
        if len(self._urls) == self._url_index:
            return {"img_url": self._default_url}
        return {"img_url": self._urls[list(self._urls.keys())[self._url_index]]["url"]}

    def img_update_handler(self, event):
        """handle new urls of Strava images"""

        # Append new images to the urls dict, keyed by a url hash.
        for img_url in event.data["img_urls"]:
            if self.is_url_valid(url=img_url["url"]):
                self._urls[md5(img_url["url"].encode()).hexdigest()] = {**img_url}

        # Ensure the urls dict is sorted by date and truncated to max # images.
        self._urls = dict(
                [url for url in sorted(self._urls.items(), key=lambda k_v:
                                       k_v[1]["date"])][-self._max_images :])

        self._pickle_urls()
        return

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self._default_enabled

    async def async_added_to_hass(self):
        self.hass.bus.async_listen(CONF_IMG_UPDATE_EVENT, self.img_update_handler)

    async def async_will_remove_from_hass(self):
        await super().async_will_remove_from_hass()

