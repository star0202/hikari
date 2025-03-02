# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021 davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Events that fire when something occurs within a guild."""

from __future__ import annotations

__all__: typing.List[str] = [
    "GuildEvent",
    "GuildVisibilityEvent",
    "GuildAvailableEvent",
    "GuildUnavailableEvent",
    "GuildLeaveEvent",
    "GuildUpdateEvent",
    "BanEvent",
    "BanCreateEvent",
    "BanDeleteEvent",
    "EmojisUpdateEvent",
    "IntegrationEvent",
    "IntegrationCreateEvent",
    "IntegrationDeleteEvent",
    "IntegrationUpdateEvent",
    "PresenceUpdateEvent",
]

import abc
import typing

import attr

from hikari import intents
from hikari import traits
from hikari.events import base_events
from hikari.events import shard_events
from hikari.internal import attr_extensions

if typing.TYPE_CHECKING:
    from hikari import channels as channels_
    from hikari import emojis as emojis_
    from hikari import guilds
    from hikari import presences as presences_
    from hikari import snowflakes
    from hikari import users
    from hikari import voices
    from hikari.api import shard as gateway_shard


@base_events.requires_intents(
    intents.Intents.GUILDS, intents.Intents.GUILD_BANS, intents.Intents.GUILD_EMOJIS, intents.Intents.GUILD_PRESENCES
)
class GuildEvent(shard_events.ShardEvent, abc.ABC):
    """Event base for any guild-bound event."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def guild_id(self) -> snowflakes.Snowflake:
        """ID of the guild that this event relates to.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The ID of the guild that relates to this event.
        """

    async def fetch_guild(self) -> guilds.RESTGuild:
        """Perform an API call to get the guild that this event relates to.

        Returns
        -------
        hikari.guilds.RESTGuild
            The guild this event occurred in.
        """
        return await self.app.rest.fetch_guild(self.guild_id)

    async def fetch_guild_preview(self) -> guilds.GuildPreview:
        """Perform an API call to get the preview of the event's guild.

        Returns
        -------
        hikari.guilds.GuildPreview
            The preview of the guild this event occurred in.
        """
        return await self.app.rest.fetch_guild_preview(self.guild_id)

    def get_guild(self) -> typing.Optional[guilds.GatewayGuild]:
        """Get the cached guild that this event relates to, if known.

        If not known, this will return `builtins.None` instead.

        Returns
        -------
        typing.Optional[hikari.guilds.GatewayGuild]
            The guild this event relates to, or `builtins.None` if not known.
        """
        if not isinstance(self.app, traits.CacheAware):
            return None

        return self.app.cache.get_available_guild(self.guild_id) or self.app.cache.get_unavailable_guild(self.guild_id)


@base_events.requires_intents(intents.Intents.GUILDS)
class GuildVisibilityEvent(GuildEvent, abc.ABC):
    """Event base for any event that changes the visibility of a guild.

    This includes when a guild becomes available after an outage, when a
    guild becomes available on startup, when a guild becomes unavailable due
    to an outage, when the user is kicked/banned/leaves a guild, or when
    the user joins a new guild.
    """

    __slots__: typing.Sequence[str] = ()


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILDS)
class GuildAvailableEvent(GuildVisibilityEvent):
    """Event fired when a guild becomes available.

    This will occur on startup, after outages, and if the bot joins a new guild.

    !!! note
        Some fields like `members` and `presences` are included here but not on
        the other `GuildUpdateEvent` and `GuildUnavailableEvent` guild visibility
        event models.
    """

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild: guilds.GatewayGuild = attr.field()
    """Guild that just became available.

    Returns
    -------
    hikari.guilds.Guild
        The guild that relates to this event.
    """

    emojis: typing.Mapping[snowflakes.Snowflake, emojis_.KnownCustomEmoji] = attr.field(repr=False)
    """Mapping of emoji IDs to the emojis in the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.emojis.KnownCustomEmoji]
        The emojis in the guild.
    """

    roles: typing.Mapping[snowflakes.Snowflake, guilds.Role] = attr.field(repr=False)
    """Mapping of role IDs to the roles in the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.guilds.Role]
        The roles in the guild.
    """

    channels: typing.Mapping[snowflakes.Snowflake, channels_.GuildChannel] = attr.field(repr=False)
    """Mapping of channel IDs to the channels in the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.channels.GuildChannel]
        The channels in the guild.
    """

    members: typing.Mapping[snowflakes.Snowflake, guilds.Member] = attr.field(repr=False)
    """Mapping of user IDs to the members in the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.guilds.Member]
        The members in the guild.
    """

    presences: typing.Mapping[snowflakes.Snowflake, presences_.MemberPresence] = attr.field(repr=False)
    """Mapping of user IDs to the presences for the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.presences.MemberPresence]
        The member presences in the guild.
    """

    voice_states: typing.Mapping[snowflakes.Snowflake, voices.VoiceState] = attr.field(repr=False)
    """Mapping of user IDs to the voice states active in this guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.voices.VoiceState]
        The voice states active in the guild.
    """

    chunk_nonce: typing.Optional[str] = attr.field(repr=False, default=None)
    """Nonce used to request the member chunks for this guild.

    This will be `builtins.None` if no chunks were requested.

    !!! note
        This is a synthetic field.

    Returns
    -------
    typing.Optional[builtins.str]
        The nonce used to request the member chunks.
    """

    @property
    def app(self) -> traits.RESTAware:
        # <<inherited docstring from Event>>.
        return self.guild.app

    @property
    def guild_id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from GuildEvent>>.
        return self.guild.id


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILDS)
class GuildLeaveEvent(GuildVisibilityEvent):
    """Event fired when the bot is banned/kicked/leaves a guild.

    This will also fire if the guild was deleted.
    """

    app: traits.RESTAware = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from Event>>.

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild_id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from GuildEvent>>.

    old_guild: typing.Optional[guilds.GatewayGuild] = attr.field()
    """The old guild object.

    This will be `builtins.None` if the guild missing from the cache.
    """

    if typing.TYPE_CHECKING:
        # This should always fail.
        async def fetch_guild(self) -> typing.NoReturn:
            ...


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILDS)
class GuildUnavailableEvent(GuildVisibilityEvent):
    """Event fired when a guild becomes unavailable because of an outage."""

    app: traits.RESTAware = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from Event>>.

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild_id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from GuildEvent>>.


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILDS)
class GuildUpdateEvent(GuildEvent):
    """Event fired when an existing guild is updated."""

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    old_guild: typing.Optional[guilds.GatewayGuild] = attr.field()
    """The old guild object.

    This will be `builtins.None` if the guild missing from the cache.
    """

    guild: guilds.GatewayGuild = attr.field()
    """Guild that was just updated.

    Returns
    -------
    hikari.guilds.Guild
        The guild that relates to this event.
    """

    emojis: typing.Mapping[snowflakes.Snowflake, emojis_.KnownCustomEmoji] = attr.field(repr=False)
    """Mapping of emoji IDs to the emojis in the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.emojis.KnownCustomEmoji]
        The emojis in the guild.
    """

    roles: typing.Mapping[snowflakes.Snowflake, guilds.Role] = attr.field(repr=False)
    """Mapping of role IDs to the roles in the guild.

    Returns
    -------
    typing.Mapping[hikari.snowflakes.Snowflake, hikari.guilds.Role]
        The roles in the guild.
    """

    @property
    def app(self) -> traits.RESTAware:
        # <<inherited docstring from Event>>.
        return self.guild.app

    @property
    def guild_id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from GuildEvent>>.
        return self.guild.id


@base_events.requires_intents(intents.Intents.GUILD_BANS)
class BanEvent(GuildEvent, abc.ABC):
    """Event base for any guild ban or unban."""

    __slots__: typing.Sequence[str] = ()

    @property
    def app(self) -> traits.RESTAware:
        # <<inherited docstring from Event>>.
        return self.user.app

    @property
    @abc.abstractmethod
    def user(self) -> users.User:
        """User that this ban event affects.

        Returns
        -------
        hikari.users.User
            The user that this event concerns.
        """

    async def fetch_user(self) -> users.User:
        """Perform an API call to fetch the user this ban event affects.

        Returns
        -------
        hikari.users.User
            The user affected by this event.
        """
        return await self.app.rest.fetch_user(self.user)


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_BANS)
class BanCreateEvent(BanEvent):
    """Event that is fired when a user is banned from a guild."""

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild_id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from GuildEvent>>.

    user: users.User = attr.field()
    # <<inherited docstring from BanEvent>>.

    @property
    def user_id(self) -> snowflakes.Snowflake:
        """User ID of the user that got banned.

        Returns
        -------
        hikari.snowflakes.Snowflake
            ID of the user the event concerns.
        """
        return self.user.id

    async def fetch_ban(self) -> guilds.GuildBan:
        """Perform an API call to fetch the details about this ban.

        This will include the optionally defined audit log reason for the
        ban.

        Returns
        -------
        hikari.guilds.GuildBan
            The ban details.
        """
        return await self.app.rest.fetch_ban(self.guild_id, self.user)


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_BANS)
class BanDeleteEvent(BanEvent):
    """Event that is fired when a user is unbanned from a guild."""

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild_id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from GuildEvent>>.

    user: users.User = attr.field()
    # <<inherited docstring from BanEvent>>.


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_EMOJIS)
class EmojisUpdateEvent(GuildEvent):
    """Event that is fired when the emojis in a guild are updated."""

    app: traits.RESTAware = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from Event>>.

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    guild_id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from GuildEvent>>.

    old_emojis: typing.Optional[typing.Sequence[emojis_.KnownCustomEmoji]] = attr.field()
    """Sequence of all old emojis in this guild.

    This will be `builtins.None` if it's missing from the cache.
    """

    emojis: typing.Sequence[emojis_.KnownCustomEmoji] = attr.field()
    """Sequence of all emojis in this guild.

    Returns
    -------
    typing.Sequence[emojis_.KnownCustomEmoji]
        All emojis in the guild.
    """

    async def fetch_emojis(self) -> typing.Sequence[emojis_.KnownCustomEmoji]:
        """Perform an API call to retrieve an up-to-date view of the emojis.

        Returns
        -------
        typing.Sequence[emojis_.KnownCustomEmoji]
            All emojis in the guild.
        """
        return await self.app.rest.fetch_guild_emojis(self.guild_id)


@base_events.requires_intents(intents.Intents.GUILD_INTEGRATIONS)
class IntegrationEvent(GuildEvent, abc.ABC):
    """Event base for any integration related events."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def application_id(self) -> typing.Optional[snowflakes.Snowflake]:
        """ID of Discord bot application this integration is connected to.

        Returns
        -------
        typing.Optional[hikari.snowflakes.Snowflake]
            The ID of Discord bot application this integration is connected to.
        """

    @property
    @abc.abstractmethod
    def id(self) -> snowflakes.Snowflake:
        """ID of the integration.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The ID of the integration.
        """

    async def fetch_integrations(self) -> typing.Sequence[guilds.Integration]:
        """Perform an API call to fetch some number of guild integrations.

        !!! warning
            The results of this are not clearly defined by Discord. The current
            behaviour appears to be that only the first 50 integrations actually
            get returned. Discord have made it clear that they are not willing
            to fix this in
            https://github.com/discord/discord-api-docs/issues/1990.

        Returns
        -------
        typing.Sequence[hikari.guilds.Integration]
            Some possibly random subset of the integrations in a guild,
            probably.
        """
        return await self.app.rest.fetch_integrations(self.guild_id)


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_INTEGRATIONS)
class IntegrationCreateEvent(IntegrationEvent):
    """Event that is fired when an integration is created in a guild."""

    app: traits.RESTAware = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from Event>>.

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    integration: guilds.Integration = attr.field()
    """Integration that was created."""

    @property
    def application_id(self) -> typing.Optional[snowflakes.Snowflake]:
        # <<inherited docstring from IntegrationEvent>>.
        return self.integration.application.id if self.integration.application else None

    @property
    def guild_id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from ShardEvent>>.
        return self.integration.guild_id

    @property
    def id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from IntegrationEvent>>
        return self.integration.id


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_INTEGRATIONS)
class IntegrationDeleteEvent(IntegrationEvent):
    """Event that is fired when an integration is deleted in a guild."""

    app: traits.RESTAware = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from Event>>.

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    application_id: typing.Optional[snowflakes.Snowflake] = attr.field()
    # <<inherited docstring from IntegrationEvent>>.

    guild_id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from ShardEvent>>.

    id: snowflakes.Snowflake = attr.field()
    # <<inherited docstring from IntegrationEvent>>


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_INTEGRATIONS)
class IntegrationUpdateEvent(IntegrationEvent):
    """Event that is fired when an integration is updated in a guild."""

    app: traits.RESTAware = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from Event>>.

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    integration: guilds.Integration = attr.field()
    """Integration that was updated."""

    @property
    def application_id(self) -> typing.Optional[snowflakes.Snowflake]:
        # <<inherited docstring from IntegrationEvent>>.
        return self.integration.application.id if self.integration.application else None

    @property
    def guild_id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from GuildEvent>>.
        return self.integration.guild_id

    @property
    def id(self) -> snowflakes.Snowflake:
        # <<inherited docstring from IntegrationEvent>>
        return self.integration.id


@attr_extensions.with_copy
@attr.define(kw_only=True, weakref_slot=False)
@base_events.requires_intents(intents.Intents.GUILD_PRESENCES)
class PresenceUpdateEvent(shard_events.ShardEvent):
    """Event fired when a user in a guild updates their presence in a guild.

    Sent when a guild member changes their presence in a specific guild.

    If the user is changed (e.g. new username), then this may fire many times
    (once for every guild the bot is part of). This is a limitation of how
    Discord implements their event system, unfortunately.

    Furthermore, if the target user is a bot and the bot only updates their
    presence on specific shards, this will only fire for the corresponding
    shards that saw the presence update.
    """

    shard: gateway_shard.GatewayShard = attr.field(metadata={attr_extensions.SKIP_DEEP_COPY: True})
    # <<inherited docstring from ShardEvent>>.

    old_presence: typing.Optional[presences_.MemberPresence] = attr.field()
    """The old member presence object.

    This will be `builtins.None` if the member presence missing from the cache.
    """

    presence: presences_.MemberPresence = attr.field()
    """Member presence.

    Returns
    -------
    hikari.presences.MemberPresence
        Presence for the user in this guild.
    """

    user: typing.Optional[users.PartialUser] = attr.field()
    """User that was updated.

    This is a partial user object that only contains the fields that were
    updated on the user profile.

    Will be `builtins.None` if the user itself did not change.
    This is always the case if the user only updated their member
    representation and did not change their user profile directly.

    Returns
    -------
    typing.Optional[hikari.users.PartialUser]
        The partial user containing the updated fields.
    """

    @property
    def app(self) -> traits.RESTAware:
        # <<inherited docstring from Event>>.
        return self.presence.app

    @property
    def user_id(self) -> snowflakes.Snowflake:
        """User ID of the user that updated their presence.

        Returns
        -------
        hikari.snowflakes.Snowflake
            ID of the user the event concerns.
        """
        return self.presence.user_id

    @property
    def guild_id(self) -> snowflakes.Snowflake:
        """Guild ID that the presence was updated in.

        Returns
        -------
        hikari.snowflakes.Snowflake
            ID of the guild the event occurred in.
        """
        return self.presence.guild_id

    def get_user(self) -> typing.Optional[users.User]:
        """Get the full cached user, if it is available.

        Returns
        -------
        typing.Optional[hikari.users.User]
            The full cached user, or `builtins.None` if not cached.
        """
        if not isinstance(self.app, traits.CacheAware):
            return None

        return self.app.cache.get_user(self.user_id)

    async def fetch_user(self) -> users.User:
        """Perform an API call to fetch the user this event concerns.

        Returns
        -------
        hikari.users.User
            The user affected by this event.
        """
        return await self.app.rest.fetch_user(self.user_id)
