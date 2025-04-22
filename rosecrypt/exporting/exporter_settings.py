"""
Exporter Settings

Defines the :class:`ExporterSettings`, which holds configuration values
that influence how dungeon data is exported to external formats such as
Foundry VTT. These settings are typically set via the GUI interface.
"""

from dataclasses import dataclass

from rosecrypt.rendering.rendering_settings import RenderingSettings

@dataclass
class ExporterSettings:
    """
    Configuration for dungeon export behavior.

    These settings affect how exported data is formatted, such as
    image padding and rendering parameters for Foundry VTT.

    :param rendering_settings: Rendering settings that affect image generation.
    :type rendering_settings: RenderingSettings
    """

    def __init__(self, rendering_settings: RenderingSettings):
        """
        Initializes export configuration with rendering options and defaults.

        :param rendering_settings: Shared rendering settings used by the exporter.
        :type rendering_settings: RenderingSettings
        """
        self.rendering_settings = rendering_settings

        self.foundry_padding = 0.25 # Padding to add to foundry exported scenes

    @classmethod
    def from_gui(
            cls,
            rendering_settings: RenderingSettings
    ) -> 'ExporterSettings':
        """
        Factory method to create exporter settings from GUI inputs.

        :param rendering_settings: Rendering settings configured via the GUI.
        :type rendering_settings: RenderingSettings

        :return: A configured ExporterSettings instance.
        :rtype: ExporterSettings
        """
        settings = cls(rendering_settings=rendering_settings)
        return settings
