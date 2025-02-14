from sema4ai.actions import action
import edge_tts
import asyncio
import pygame
from pathlib import Path
import tempfile
import contextlib


class AudioPlayer:
    def __init__(self):
        self.initialized = False

    def initialize(self):
        if not self.initialized:
            pygame.mixer.init()
            self.initialized = True

    def cleanup(self):
        if self.initialized:
            pygame.mixer.quit()
            self.initialized = False

    @contextlib.contextmanager
    def play_session(self):
        try:
            self.initialize()
            yield
        finally:
            self.cleanup()

    def play_audio(self, audio_file: Path):
        pygame.mixer.music.load(str(audio_file))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


class TextToSpeech:
    def __init__(self, voice="en-US-ChristopherNeural", rate="+15%"):
        self.voice = voice
        self.rate = rate

    async def generate_audio(self, text: str, voice: str, output_file: Path):
        communicate = edge_tts.Communicate(text, voice=voice, rate=self.rate)
        await communicate.save(str(output_file))


@action
def talk(text: str, voice: str) -> str:
    """Action to convert text to audio and play it immediately. Keep the inputs conversation friendly.

    Args:
        text: Text to convert to audio and play.
        voice: Voice to use for the audio.
    Returns:
        str: Result of the action.
    """
    # Create temporary file for audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        # Generate audio
        tts = TextToSpeech()
        asyncio.run(tts.generate_audio(text, voice, temp_path))

        # Play audio
        player = AudioPlayer()
        with player.play_session():
            player.play_audio(temp_path)

        return "Audio playback complete"

    finally:
        # Cleanup temporary file
        temp_path.unlink(missing_ok=True)
