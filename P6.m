
.......................................................................................
% Comprueba si estamos ejecutando en MATLAB o en Octave
if (exist('OCTAVE_VERSION', 'builtin') ~= 0)
% Estamos en Octave
  pkg load signal;
end
% Menú principal
opcion = 0;
while opcion ~= 9
  %opcion = inpul('Seleccione una opción:\tl 1. Grabar audio\n 2. Reproducir audio\n 3. Graficar audio\tl 4. Salil'ln');
  % Menú de opciones
  disp('Seleccione una opción:')
  disp('1. Grabar')
  disp('2. Reproducir')
  disp('3. Graficar')
  disp('4. Graficar densidad')
  disp('5. Graficar filtro RFI')
  disp('6. Graficar filtro RII')
  disp('7. Transdormada Z')
  disp('8. Transf. de coseno discreta')
  disp('9. Salir')
  opcion = input('lngrese su elección:');
    switch opcion
      case 1
        % Grabación de audio
        try
          duracion = input('lngrese la duración de la grabación en segundos:');
          disp('Comenzando la grabación .. .');
          recObj = audiorecorder;
          recordblocking(recObj, duracion);
          disp('Grabación finalizada.');
          data = getaudiodata(recObj);
          audiowrite('audio.wav', data, recObj.SampleRate);
          disp('Archivo de audio grabado correctamente.');
        catch
          disp('Error al grabar el audio.');
        end
      case 2
        % Reproducción de audio
        try
          [data, fs] = audioread('audio.wav');
          sound(data, fs);
        catch
          disp('Error al reproducir el audio.');
        end
      case 3
        % Gráfico de audio
        try
          [data, fs] = audioread('audio.wav');
          tiempo = linspace(0, length(data)/fs, length(data));
          plot(tiempo, data);
          xlabel('Tiempo (s)');
          ylabel(' Amplitud');
          litle('Audio');
        catch
          disp('Error al graficar el audio.');
        end
      case 4
        % Graficando espectro de frecuencia
        try
        disp('Graficando espectro de frecuencia .. .');
        [audio, Fs] = audioread('audio.wav'); % Lee la seiial desde el archivo .wav
        N = length(audio); % Número de muestras de la señal
        f = linspace(0, Fs/2, N/2+1 ); % Vector de frecuencias
        ventana = hann(N); % Ventana de Hann para reducir el efecto de las discontinuidades al calcular la FF T
        Sxx = pwelch(audio, ventana, 0, N, Fs); % Densidad espectral de potencia
        plot(f, 10*log10(Sxx(1:N/2+1))); % Grafica el espectro de frecuencia en dB
        xlabel('Frecuencia (Hz)');
        ylabel('Densidad espectral de potencia (dB/Hz)');
        litle('Espectro de frecuencia de la seiial grabada');
        catch
          disp('Error al graficar el audio.');
        end
      case 5
        try
        [input_signal, fs] = audioread('audio.wav');
        fc = 1000; % frecuencia de corte
        bw = 500; % ancho de banda
        Wn = [fc-bw/2, fc+bw/2]/(fs/2);
        [b, a] = butter(2, Wn);
        % Diseñar el filtro Notch de segundo orden para eliminar interferencias
        fn = 1200; % frecuencia de interferencia
        Wn_notch = fn/(fs/2);
        [b_notch, a_notch] = pei_tseng_notch(Wn_notch, 0.1);
        % Combinar los dos filtros en serie
        b_total = conv(b, b_notch);
        a_total = conv(a, a_notch);
        % Aplicar el filtro RFI a la señal de audio
        filtered_signal_RFI = filter(b_total, a_total, input_signal);
        % Graficar la señal de audio filtrada con el filtro RFI
        t = 0:1/fs:(length(filtered_signal_RFI)-1)/fs;
        figure();
        plot(t, filtered_signal_RFI);
        xlabel('Tiempo (s)');
        ylabel('Amplitud');
        title('Señal filtrada con filtro RFI');
        catch
          disp('Error al graficar los filtros.');
        end
      case 6
        try
        [input_signal, fs] = audioread('audio.wav');
        fc = 1000; % frecuencia de corte
        bw = 500; % ancho de banda
        Wn = [fc-bw/2, fc+bw/2]/(fs/2);
        [b, a] = butter(2, Wn);
        % Diseñar el filtro Notch de segundo orden para eliminar interferencias
        fn = 1200; % frecuencia de interferencia
        Wn_notch = fn/(fs/2);
        [b_notch, a_notch] = pei_tseng_notch(Wn_notch, 0.1);
        % Combinar los dos filtros en serie
        b_total = conv(b, b_notch);
        a_total = conv(a, a_notch);
        % Aplicar el filtro RFI a la señal de audio
        filtered_signal_RFI = filter(b_total, a_total, input_signal);
        % Diseñar el filtro RII
        fc = 1000; % frecuencia de corte
        gain = 20; % ganancia en la banda de paso
        % Calcule la frecuencia normalizada
        Wn = fc/(fs/2);
        % Diseñar el filtro Chebyshev de tercer orden con un polo real y dos polos complejos conjugados
        [b, a] = cheby1(3, gain, Wn, 'high');
        % Aplicar el filtro RII a la señal de audio
        filtered_signal_RII = filter(b, a, filtered_signal_RFI);
        % Graficar la señal de audio filtrada con el filtro RII
        t = 0:1/fs:(length(filtered_signal_RII)-1)/fs;
        figure();
        plot(t, filtered_signal_RII);
        xlabel('Tiempo (s)');
        ylabel('Amplitud');
        title('Señal filtrada con filtro RII');
        catch
          disp('Error al graficar los filtros.');
        end

      case 7
        try
        % Leer archivo de audio WAV
        [x, fs] = audioread('audio.wav');

        % Convertir la señal monoaural
        x = mean(x, 2);

        %Calcula Transdormada Z
        z = tf(x, 1);

        %Obtener coeficientes de la Transformada Z
        [b, a] = tfdata(z, "vector");

        %Aplicar Transformada Z al archivo de audio
        y = filter(b, a, x);

        % Graficar señal original y señal con Transformada Z aplicada
        t = 0:1/fs:(length(x)-1)/fs;
        subplot(2, 1, 1);
        plot(t, x);
        xlabel("Tiempo(s)");
        ylabel("Amplitud");
        title("Señal Original");

        subplot(2, 1, 2);
        plot(t, y);
        xlabel("Tiempo(s)");
        ylabel("Amplitud");
        title("Señal con Transformada Z aplicada");

        %Escribir archivo de audio WAV con Transformada Z aplicada
        audiowrite("archivo_audio_con_Z.wav", y, fs);
        catch
          disp('Error al aplicar transf.Z');
        end

      case 8
        try
        % Leer archivo de audio WAV
        [y, fs] = audioread('audio_menu.wav');

        dct_y = dct(y);

        umbral = 0.1;

        %Obtener coeficientes de la Transformada Z
        dct_y_comprimido = dct_y.*(abs(dct_y)>umbral);

        %Aplicar Transformada Z al archivo de audio
        y_comprimido = idct(dct_y_comprimido);

        % Graficar señal original y señal con Transformada Z aplicada
        t = (0:length(y)-1)/fs;
        t_comp = (0:length(y_comprimido)-1)/fs;

        subplot(2, 1, 1);
        plot(t, y);
        xlabel("Tiempo(s)");
        ylabel("Amplitud");
        title("Archivo de audio inicial");

        subplot(2, 1, 2);
        plot(t_comp, y_comprimido);
        xlabel("Tiempo(s)");
        ylabel("Amplitud");
        title("Archivo de audio comprimido");

        %Escribir archivo de audio WAV con Transformada Z aplicada
        audiowrite("archivo_audio_con_DCT.wav", y_comprimido, fs);

        catch
          disp('Error al aplicar transf. de coseno discreta');
        end

      case 9
        try
        % Salir
        disp('Saliendo del programa .. .');
        catch
          disp('Error .');
        end
      otherwise
      disp('Opción no válida.');
  end
end







