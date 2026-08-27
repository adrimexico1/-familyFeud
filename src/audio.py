import os
import math
import struct
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QObject

class AudioManager(QObject):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
        os.makedirs(self.resources_dir, exist_ok=True)
        
        self.correct_path = os.path.join(self.resources_dir, "correct.wav")
        self.strike_path = os.path.join(self.resources_dir, "strike.wav")
        self.buzzer_path = os.path.join(self.resources_dir, "buzzer.wav")
        
        # Generar los archivos si no existen
        self._ensure_sounds_exist()
        
        # Inicializar efectos de sonido de PySide6
        self.sound_correct = QSoundEffect()
        self.sound_correct.setSource(QUrl.fromLocalFile(self.correct_path))
        self.sound_correct.setVolume(1.0)
        
        self.sound_strike = QSoundEffect()
        self.sound_strike.setSource(QUrl.fromLocalFile(self.strike_path))
        self.sound_strike.setVolume(1.0)
        
        self.sound_buzzer = QSoundEffect()
        self.sound_buzzer.setSource(QUrl.fromLocalFile(self.buzzer_path))
        self.sound_buzzer.setVolume(1.0)

    def play_correct(self):
        self.sound_correct.play()

    def play_strike(self):
        self.sound_strike.play()

    def play_buzzer(self):
        self.sound_buzzer.play()

    def _ensure_sounds_exist(self):
        """Asegura que los efectos de sonido existan autogenerándolos si es necesario."""
        if not os.path.exists(self.correct_path):
            self._generate_correct_sound(self.correct_path)
        if not os.path.exists(self.strike_path):
            self._generate_strike_sound(self.strike_path)
        if not os.path.exists(self.buzzer_path):
            self._generate_buzzer_sound(self.buzzer_path)

    def _write_wav(self, filepath, samples, sample_rate=44100):
        """Escribe una lista de muestras a un archivo WAV PCM de 16 bits mono."""
        data_size = len(samples) * 2
        file_size = 36 + data_size
        
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', file_size, b'WAVE', b'fmt ', 16,
            1, 1, sample_rate, sample_rate * 2,
            2, 16, b'data', data_size
        )
        
        with open(filepath, 'wb') as f:
            f.write(header)
            for s in samples:
                # Limitar los valores para evitar desbordamiento
                val = int(max(-32768, min(32767, s)))
                f.write(struct.pack('<h', val))

    def _generate_correct_sound(self, filepath):
        """Genera un sonido de respuesta correcta (arpegio ascendente brillante)."""
        sample_rate = 44100
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_duration = 0.12  # Duración de cada nota en segundos
        fade_duration = 0.05
        samples = []
        
        total_samples = int(sample_rate * note_duration * len(notes))
        
        for i in range(total_samples):
            t = i / sample_rate
            note_idx = int(t / note_duration)
            if note_idx >= len(notes):
                note_idx = len(notes) - 1
            
            freq = notes[note_idx]
            
            # Generar onda sinusoidal
            val = math.sin(2 * math.pi * freq * t)
            
            # Agregar una onda armónica superior para brillo
            val += 0.3 * math.sin(2 * math.pi * (freq * 2) * t)
            
            # Envoltura de volumen
            # Desvanecimiento al final de todo el sonido
            time_left = (total_samples - i) / sample_rate
            if time_left < fade_duration:
                volume = time_left / fade_duration
            else:
                volume = 1.0
                
            # Pequeño transitorio de ataque por nota
            local_t = t - (note_idx * note_duration)
            if local_t < 0.01:
                volume *= (local_t / 0.01)
                
            samples.append(val * 16000 * volume)
            
        self._write_wav(filepath, samples, sample_rate)

    def _generate_strike_sound(self, filepath):
        """Genera un zumbido fuerte para errores (Strike X)."""
        sample_rate = 44100
        duration = 0.8  # Segundos
        samples = []
        
        total_samples = int(sample_rate * duration)
        
        for i in range(total_samples):
            t = i / sample_rate
            # Mezcla de frecuencias bajas y ásperas (onda cuadrada distorsionada)
            freq1 = 110.0  # La2
            freq2 = 113.0  # Ligeramente desafinado para efecto corus/fase
            
            # Onda cuadrada aproximada
            val1 = 1.0 if math.sin(2 * math.pi * freq1 * t) > 0 else -1.0
            val2 = 1.0 if math.sin(2 * math.pi * freq2 * t) > 0 else -1.0
            
            val = (val1 + val2) * 0.5
            # Añadir armónico para hacerlo más chillón
            val += 0.25 * math.sin(2 * math.pi * 330.0 * t)
            
            # Envoltura (ataque rápido, decaimiento lineal)
            volume = 1.0
            if t > 0.6:
                volume = (duration - t) / 0.2
            
            samples.append(val * 12000 * volume)
            
        self._write_wav(filepath, samples, sample_rate)

    def _generate_buzzer_sound(self, filepath):
        """Genera un sonido de zumbador doble para dinero rápido."""
        sample_rate = 44100
        samples = []
        
        # Dos ráfagas de zumbador
        burst_duration = 0.25
        silence_duration = 0.1
        
        def get_buzzer_sample(t):
            # Frecuencia áspera
            freq = 145.0
            val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            val += 0.5 * (1.0 if math.sin(2 * math.pi * (freq * 1.5) * t) > 0 else -1.0)
            return val * 0.6
            
        # Ráfaga 1
        num_burst1 = int(sample_rate * burst_duration)
        for i in range(num_burst1):
            t = i / sample_rate
            samples.append(get_buzzer_sample(t) * 14000)
            
        # Silencio
        num_silence = int(sample_rate * silence_duration)
        for _ in range(num_silence):
            samples.append(0)
            
        # Ráfaga 2
        num_burst2 = int(sample_rate * burst_duration)
        for i in range(num_burst2):
            t = i / sample_rate
            samples.append(get_buzzer_sample(t) * 14000)
            
        self._write_wav(filepath, samples, sample_rate)
