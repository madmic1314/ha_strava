# Integration Abandonded - do not add to Home Assistant, it will fail
With the last set of changes required, I've decided to no longer try and maintain integration. There will be no fixes or replies to issues - I leave this here in case anyone wants to fork it and take over.

I used the original integration as I makde a gadget for my wife's running that sat on her desk at home as a bit of fun. She no longer works from home often, so this has fallen into disuse, especially with the drive to save as much electricity as possible, this now sits in a drawer.

I'm a technologist by day, but never learnt to code beyond VBA and a bit of VB - was also pretty good at the OPL Language used on the Psion devices - so dropping into this integration at this level is too much a learning curve. Unfortunately, I have too much else to do outside of work to learn try and Python to the level of understanding required to carry this integration on. The rate of breaking changes that come from the rapid pace of HA means I simply can't keep up - I did try.

Hopefully someone will pick this up and run with it (see what I did there?), else "My battery is low and it’s getting dark." -Opportunity Rover


# Strava Home Assistant Integration

NOTE: You MUST remove the HA_Strava integration from Home Assistant integration, HACS Integration, HACS Custom Repository and reboot HA before adding this.

Custom Component to integrate Activity Data from Strava into Home Assistant.

This is a fork from Codingcyclist <https://github.com/codingcyclist/ha_strava> in an attempt to keep the integration alive - I take no credit for his hard work. I'm not a coder and the best you'll get from me is copy + paste, but happy to accept contributions and help from the community.

## Features

* Gives you access to **up to 10 of your most recent activities** in Strava.
* Supports both the **metric and the imperial** unit system
* Activity data in Home Assistant **auto-updates** whenever you add, modify, or delete activities on Strava
* Exposes **5 customizable sensor entities** for each Strava activity
* **Easy set-up**: only enter your Strava Client-ID and -secret and you're ready to go

![sensor_overview image](sensor_overview.png)

For every Strava activity, the Strava Home Assistant Integration creates a **device entity** in Home Assistant (max 10 activities). Each of these virtual device entities exposes **five sensor entities** which you can customize to display one of the following **activity KPIs**:

* Duration (Minutes),
* Pace (Minutes/Mile ; Minutes/Km)
* Speed (Miles/Hour; Km/Hour)
* Distance (Miles; Km)
* \# Kudos
* Calories (kcal),
* Elevation Gain (Feet, Meter)
* Power (Watts)
* \# Trophies

**One additional sensor entity** will be available for every Strava activity to display Date & Title of the underlying activity. To map a name to an activities's GPS start location, Strava Home Assistant relies on the free API at [geocode.xyz](https://geocode.xyz). In the event that Strava Home Assistant cannot fetch a location name from geocode.xyz, it'll put "Paradise City" as the default location.

Since every Strava activity gets its own virtual device, you can use the underlying sensor data in your **Dashboards and Automations**, just as you'd use any other sensor data in Home Assistant. To learn how to display information about your most recent Strava Activities, please reference the **UI-configuration example** below.

## Installation

### First, set up remote access to your Home Assistant Installation

To use the Strava Home Assistant integration, your Home Assistant Instance must be accessible from an **External URL** (i.e. Remote Access). Without remote access, the integration won't be able to pull data from Strava. To learn how to set up Remote Access for Home Assistant, please visit the [Official Documentation](https://www.home-assistant.io/docs/configuration/remote/)

_If you use NabuCasa (and I strongly advise you to support this project!) then do this configuration from your Nabucasa URL. You can find this under Configuration -> "Home Assistant Cloud"_

### Second, obtain your Strava API credentials

After you've set up remote access and configured the External URL for your Home Assistant instance, head over to your **Strava Profile**. Under "**Settings**", go to "**My API Application**", follow the steps in the configuration wizard, and eventually obtain your Strava API credentials (ID + secret). We need those credentials during the final installation step.

**!!! IMPORTANT !!!** It is essential that the **Authorization Callback Domain** which you set for your Strava API matches the domain of your **Home Assistant External URL**

### Third, add the Strava Home Assistant Integration to your Home Assistant Installation

As of now, the Strava Home Assistant Integration can only be installed as a custom repository through the Home Assistant Community Store (HACS). The installation process is super easy, check out my **5-minute tutorial on how to install Custom Components in HACS** [here](https://medium.com/@codingcyclist/how-to-install-any-custom-component-from-github-in-less-than-5-minutes-ad84e6dc56ff)

### Fourth, make a connection between your Strava account and Home Assistant

Now is the time to fire up the Strava Home Assistant Integration for the first time and make a connection between Strava and your Home Assistant Instance.

![ha_strava_install image](ha_strava_install.gif)

From within Home Assistant, head over to `Configuration` > `Integrations` and hit the "+"-symbol at the bottom. Search for "Strava Home Assistant" and click on the icon to add the Integration to Home Assistant. You'll automatically be prompted to enter your Strava API credentials. It'll take a few seconds to complete the set-up process after you've granted all the required permissions.

## Configuration/Customization

Upon completion of the installation process, the Strava Home Assistant integration **automatically creates device- and sensor entities** for you to access data from your most recent Strava activities. The number of sensor entities varies, depending on how many of your most recent Strava activities you whish to track from within Home Assistant (5 + 1 sensors per activity). Per default, only sensor entities for the **two most recent Strava activities** are visible in Home Assistant. Please read the section below to learn how to change the number of visible sensor entities for Strava Home Assistant.

### Increase/Decrease the number of Strava activities available in Home Assistant

You can always **adjust the number of Strava activities you whish to track** from within Home Assistant (min 1; max 10).

![ha_strava_config image](ha_strava_config.gif)

Just locate the Strava Home Assistant Integration under `Configuration` > `Integrations`, click on `Options`, and use the slider to adjust the number of activities. After you've saved your settings, it might take a few minutes for Home Assistant to create the corresponding sensor entities and fetch the underlying data. The activities available in Home Assistant always correspond to the most recent ones under your Strava profile.

### Configure sensor entities for different types of Strava Activities

Strava Home Assistant exposes **five sensor entities for every Strava activity**. You customize the Strava-KPI for each of those five sensors as follows:

1. Go to `Configuration` > `Integrations`
2. Locate the Strava Home Assistant Integration and click on `Options`
3. Leave the number of concurrent Strava Activities as is and hit `SUBMIT` to proceed
4. Chose an activity type and configure the KPI-Sensor matching as you see fit
5. Hit `SUBMIT` for your changes to take effect

You can only change the sensor configuration for **one activity type at a time**. After you've completed the configuration for a given activity type, you can **start over** to change the sensor configuration for another activity type.

As of now, customization is only supported for **Ride, Run, and Hike activities**.

### Integrate Strava Activities into your Home Assistant UI

Below, you can find an example UI-configuration, which adds metrics from your two most recent Strava activities to a separate Lovelace Dashboard in Home Assistant.

![ha_strava_ui_config image](ha_strava_ui_config.gif)

```yaml
title: Home
views:
  - title: Strava
    icon: 'mdi:strava'
    path: strava
    theme: ''
    badges: []
    cards:
      - cards:
          - entity: sensor.strava_0_0
            type: entity
          - entities:
              - entity: sensor.strava_0_1
              - entity: sensor.strava_0_2
              - entity: sensor.strava_0_3
              - entity: sensor.strava_0_4
              - entity: sensor.strava_0_5
            type: glance
        type: vertical-stack
      - cards:
          - entity: sensor.strava_1_0
            type: entity
          - entities:
              - entity: sensor.strava_1_1
              - entity: sensor.strava_1_2
              - entity: sensor.strava_1_3
              - entity: sensor.strava_1_4
              - entity: sensor.strava_1_5
            type: glance
        type: vertical-stack
      - type: picture-glance
        aspect_ratio: 0%
        camera_image: camera.strava_cam
        entities: []
        image: 'https://demo.home-assistant.io/stub_config/kitchen.png'
      - entities:
          - entity: sensor.strava_stats_summary_ytd_ride_distance
          - entity: sensor.strava_stats_summary_ytd_ride_moving_time
          - entity: sensor.strava_stats_summary_all_run_distance
          - entity: sensor.strava_stats_summary_all_run_moving_time
        title: Strava - Year to Date
        type: entities
```

## Contributors

* [@codingcyclist](https://github.com/codingcyclist)

## TODO

--- NONE PLANNED ---
Learn how to code?
