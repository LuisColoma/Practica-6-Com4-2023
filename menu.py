import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
from scipy.signal import butter, cheby1, convolve, lfilter, filtfilt, iirnotch
from scipy.fftpack import dct

opcion = 0
while opcion != 8:
    print('Seleccione una opción:')
    print('1.Grabar')
    print('2.Reproducir')
    print('3.Graficar')
    print('4.Graficar Densidad')
    print('5.Filtro RFI')
    print('6.Transformada Z')
    print('7.Compresion DTC')
    print('8.Salir')
    opcion = (input('Ingrese su seleccion:'))

    if opcion == '1':
        try:
            duracion = int(input('Ingrese la duración de la grabación en segundos: '))
            print('Comenzando la grabación...')
            grabacion = sd.rec(int(duracion * 44100), samplerate=44100, channels=1)
            sd.wait()
            print('Grabación finalizada.')
            sf.write('audio_menu.wav', grabacion, 44100)
            print('Archivo de audio grabado correctamente.')
        except:
            print('Error al grabar el audio.')
    if opcion == '2':
        try:
            data, fs = sf.read('audio_menu.wav', dtype='float32')
            sd.play(data, fs)
            sd.wait()
        except:
            print('Error al grabar el audio.')
    if opcion == '3':
        try:
            # leer archivo de audio
            fs, data = wavfile.read('audio_menu.wav')

            # crear vector de tiempo
            tiempo = np.linspace(0, len(data)/fs, len(data))

            # graficar señal de audio
            plt.plot(tiempo, data)
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Amplitud')
            plt.title('Audio')
            plt.show()
        except:
            print('Error al graficar Audio')
    if opcion == '4':
        try:
            # Carga el archivo de audio
            Fs, audio = wavfile.read('audio_menu.wav')

            # Calcula la longitud de la señal de audio
            N = len(audio)

            # Define la frecuencia de muestreo y la frecuencia máxima
            f = np.linspace(0, Fs/2, N//2 + 1)

            # Define la ventana de Hann
            ventana = np.hanning(N)

            # Calcula la densidad espectral de potencia
            Sxx, f = plt.psd(audio, Fs=Fs, window=ventana, NFFT=N, pad_to=N, noverlap=0, scale_by_freq=True)

            # Grafica el espectro de frecuencia
            plt.plot(f, 10*np.log10(Sxx))
            plt.xlabel('Frecuencia (Hz)')
            plt.ylabel('Densidad espectral de potencia (dB/Hz)')
            plt.title('Espectro de Frecuencia de la señal grabada')

            # Muestra la gráfica
            plt.show()
        except:
            print('Error al graficar Audio')
    if opcion == '5':
        try:
            # Cargar el archivo de audio
            fs, input_signal = wavfile.read('audio_menu.wav')

            # Diseñar el filtro RFI
            fc = 1000  # frecuencia de corte
            bw = 500  # ancho de banda
            # Calcule la frecuencia normalizada
            Wn = (fc-bw/2)/(fs/2), (fc+bw/2)/(fs/2)
            # Diseñar el filtro Butterworth de segundo orden
            b, a = butter(2, Wn, 'bandpass')

            # Diseñar el filtro Notch de segundo orden para eliminar interferencias
            fn = 1200  # frecuencia de interferencia
            Wn_notch = fn/(fs/2)
            b_notch, a_notch = iirnotch(Wn_notch, Q=0.1)

            # Combinar los dos filtros en serie
            b_total = convolve(b, b_notch)
            a_total = convolve(a, a_notch)

            # Aplicar el filtro RFI a la señal de audio
            filtered_signal_RFI = filtfilt(b_total, a_total, input_signal)

            # Diseñar el filtro RII
            fc = 1000  # frecuencia de corte
            gain = 20  # ganancia en la banda de paso
            # Calcule la frecuencia normalizada
            Wn = fc/(fs/2)
            # Diseñar el filtro Chebyshev de tercer orden con un polo real y dos polos complejos conjugados
            b, a = cheby1(3, gain, Wn, 'high')
            # Aplicar el filtro RII a la señal de audio
            filtered_signal_RII = filtfilt(b, a, filtered_signal_RFI)

            # Graficar la señal de audio original
            t = np.arange(0, len(input_signal)/fs, 1/fs)
            plt.figure()
            plt.plot(t, input_signal)
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Amplitud')
            plt.title('Señal original')


            # Graficar la señal de audio filtrada con el filtro RFI
            t = np.arange(0, len(filtered_signal_RFI)/fs, 1/fs)
            plt.figure()
            plt.plot(t, filtered_signal_RFI)
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Amplitud')
            plt.title('Señal filtrada con filtro RFI')


            # Graficar la señal de audio filtrada con el filtro RII
            t = np.arange(0, len(filtered_signal_RII)/fs, 1/fs)
            plt.figure()
            plt.plot(t, filtered_signal_RII)
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Amplitud')
            plt.title('Señal filtrada con filtro RII')

            filtered_signal_RFI_amplified = pow(10,26)*filtered_signal_RFI
            filtered_signal_RII_amplified = pow(10,29)*filtered_signal_RII

            filtered_signal_RFI_int = (filtered_signal_RFI_amplified * 32767).astype('int16')
            wavfile.write('audio_RFI.wav', fs, filtered_signal_RFI_int)

            # Escribir archivo de audio RII en formato entero de 16 bits
            filtered_signal_RII_int = (filtered_signal_RII_amplified * 32767).astype('int16')
            wavfile.write('audio_RII.wav', fs, filtered_signal_RII_int)

            plt.show()

            r = input('¿Quieres reproducir el audio? (Y/N):')

            if r.upper() == 'Y':
                d, fss = sf.read('audio_RFI.wav', dtype='float32')
                sd.play(d, fss)
                sd.wait()
                dd, ffss = sf.read('audio_RII.wav', dtype='float32')
                sd.play(dd, ffss)
                sd.wait()
            elif r.upper() == 'N':
                print('Audio no reproducido.')
        except:
            print('Error al graficar Audio')
    if opcion == '6':
        try:
            #Leer archivo de audio WAV
            x, fs = sf.read('audio_menu.wav')

            # Convertir la señal monoaural
            #x = np.mean(x, axis=1)

            #Calcula Transdormada Z
            z = signal.tf2zpk(*signal.butter(2, [1000, 1500], btype='bandpass', fs=fs))

            #Obtener coeficientes de la Transformada Z
            b, a = signal.zpk2tf(*z)

            #Aplicar Transformada Z al archivo de audio
            y = signal.filtfilt(b, a, x)

            # Graficar señal original y señal con Transformada Z aplicada
            t = np.arange(len(x))/fs
            fig, axs = plt.subplots(2, 1, sharex=True)
            axs[0].plot(t, x)
            axs[0].set_xlabel('Tiempo(s)')
            axs[0].set_ylabel('Amplitud')
            axs[0].set_title('Señal Original')
            axs[1].plot(t, y)
            axs[1].set_xlabel('Tiempo(s)')
            axs[1].set_ylabel('Amplitud')
            axs[1].set_title('Señal con Transformada Z aplicada')
            plt.show()

            #Escribir archivo de audio WAV con Transformada Z aplicada
            sf.write("archivo_audio_con_Z.wav", y, fs)

            r = input('¿Quieres reproducir el audio? (Y/N): ')

            if r.lower() == 'y':
                d, fss = sf.read('archivo_audio_con_Z.wav', dtype='float32')
                sd.play(d, fss)
                sd.wait()
            elif r.lower() == 'n':
                print('Audio no reproducido.')
            else:
                print('Respuesta no válida.')
        except:
            print('Error al graficar Audio')
    if opcion == '7':
        try:
            ## Cargar el archivo de audio
            fs, y = wavfile.read('audio_menu.wav')

            # Realizar la DCT
            dct_y = dct(y)

            # Establecer el umbral de compresión
            umbral = 0.1

            # Comprimir la señal
            dct_y_comprimido = dct_y * (np.abs(dct_y) > umbral)
            y_comprimido = dct(dct_y_comprimido)

            # Crear los vectores de tiempo para graficar
            t = np.arange(len(y)) / fs
            t_comp = np.arange(len(y_comprimido)) / fs

            # Graficar la señal original y la comprimida
            plt.subplot(2, 1, 1)
            plt.plot(t, y)
            plt.xlabel("Tiempo [s]")
            plt.ylabel("Amplitud")
            plt.title("Archivo de audio original")
            plt.subplot(2, 1, 2)
            plt.plot(t_comp, y_comprimido)
            plt.xlabel("Tiempo [s]")
            plt.ylabel("Amplitud")
            plt.title("Archivo de audio comprimido")
            plt.show()
            # Escribir el archivo comprimido en formato WAV
            y_comprimido_amplified = y_comprimido/pow(10,10)
            sf.write("audio_comprimido.wav", y_comprimido_amplified , fs)

            # Reproducir el archivo comprimido
            r = input('¿Quieres reproducir el audio? (Y/N): ')

            if r.upper() == 'Y':
                d, fs = sf.read('audio_comprimido.wav', dtype='float32')
                sd.play(d, fs)
                sd.wait()
            else:
                print('Audio no reproducido.')
        except:
            print('Error al graficar Audio')
    if opcion == '8':
        try:
            exit(0)
        except:
            exit(0)

    