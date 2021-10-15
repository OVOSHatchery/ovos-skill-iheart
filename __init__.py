from os.path import join, dirname

from ovos_utils.parse import fuzzy_match
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    MediaType, PlaybackType, ocp_search
from pyheartradio import IHeartRadio


class IHeartRadioSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("IHeartRadio")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.MUSIC,
                                MediaType.PODCAST,
                                MediaType.RADIO]
        self.skill_icon = join(dirname(__file__), "ui", "iheart.png")

    @ocp_search()
    def search_radio(self, phrase, media_type):
        if self.location["city"]['state']["country"]["code"] != "US":
            # only works for US users
            # streams 404 in other ip addresses, this is a crude attempt of
            # avoiding that
            return  # TODO full country list

        base_score = 0

        if media_type == MediaType.RADIO:
            base_score += 20
        elif media_type == MediaType.PODCAST:
            return  # different specialized handler
        else:
            base_score -= 20

        if self.voc_match(phrase, "iheart"):
            base_score += 50  # explicit request
            phrase = self.remove_voc(phrase, "iheart")

        for ch in IHeartRadio().search_stations(phrase):
            score = base_score + \
                    fuzzy_match(ch["title"].lower(), phrase.lower()) * 100
            yield {
                "match_confidence": min(100, score),
                "media_type": MediaType.RADIO,
                "uri": ch["stream"],
                "playback": PlaybackType.AUDIO,
                "image": ch["image"],
                "bg_image": ch["image"],
                "skill_icon": self.skill_icon,
                "title": ch["title"],
                "author": "IHeartRadio",
                "length": 0
            }

    @ocp_search()
    def search_podcast(self, phrase, media_type):
        base_score = 0

        if media_type == MediaType.PODCAST:
            base_score += 20
        elif media_type == MediaType.RADIO:
            return  # different specialized handler
        else:
            base_score -= 35

        if self.voc_match(phrase, "iheart"):
            base_score += 50  # explicit request
            phrase = self.remove_voc(phrase, "iheart")

        radio = IHeartRadio()
        for podcast in radio.search_podcast(phrase):
            score = base_score + \
                    fuzzy_match(podcast["title"].lower(), phrase.lower()) * 100
            pl = [{
                    "match_confidence": min(100, score),
                    "media_type": MediaType.PODCAST,
                    "uri": ch["stream"],
                    "playback": PlaybackType.AUDIO,
                    "image": ch["image"],
                    "bg_image": ch["image"],
                    "skill_icon": self.skill_icon,
                    "skill_logo": self.skill_icon,
                    "title": ch["title"],
                    "author": podcast["title"],
                    "length": ch["duration"] * 1000,  # second to milisecond
                } for ch in radio.get_podcast_episodes(podcast["id"])]

            if pl:
                yield {
                    "match_confidence": min(100, score),
                    "media_type": MediaType.PODCAST,
                    "playlist": pl,
                    "playback": PlaybackType.AUDIO,
                    "skill_icon": self.skill_icon,
                    "image": podcast["image"],
                    "bg_image": podcast["image"],
                    "title": podcast["title"] + " (Podcast)",
                    "author": "IHeartRadio"
                }


def create_skill():
    return IHeartRadioSkill()
