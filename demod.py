import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft, fftshift
from scipy import signal
from scipy.signal import decimate, convolve

#load the binary file that has just been generated
def loadFile(filename):

        with open(filename, 'rb') as fid:
                y = np.fromfile(fid, np.uint8)
                y = y - 127.5

                return y[1:len(y)-1:2] + y[2:len(y):2]*1j

def plot_FFT_IQ(y,n0,nf,fs,f0): 

        b = (n0+nf-1)
        x_segment = y[int(n0):int(b)]
        p = fft(x_segment)
        m = max(abs(p))
        z = 20*np.log10(abs(p)/m)
        Low_freq = (f0-fs/2)
        High_freq = (f0+fs/2) 
        N = len(z)
        freq = np.arange(0,N-1,1)*(fs)/N+Low_freq

        plt.plot(freq,z[0:len(z)-1])
        plt.xlabel('Freqency [MHz]')
        plt.ylabel('Relative amplitude [dB down from max]')     
        plt.grid()
        plt.axvline(x=105.6, c='r')

	plt.savefig('plot.png')

def FM_IQ_Demod(y):

        b = signal.firls(1, [0, 0.9], [0, 1])
        d=y/abs(y)
        rd=np.real(d)
        ip=np.imag(d)
        return (rd*convolve(ip,b,'same')-ip*convolve(rd,b,'same'))/(rd**2+ip**2)


y = loadFile('capture.dat')

plot_FFT_IQ(y,1,0.002*2.e6,2.5,105.6)

x = np.arange(0,len(y),1)
y_shifted=np.multiply(y, np.transpose(np.exp(1j*2*np.pi*0.2E6*x/2.5E6)))

d = decimate(y_shifted,8,ftype='fir')

y_FM_demodulated = FM_IQ_Demod(d)

#plot_FFT_IQ(y_FM_demodulated,1,.05*2.5E6/8,2.5/8,0);


