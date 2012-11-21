import scipy
from kalman import Kalman
import numpy as np

def filterNoiseByFreq(in_signal):
    #use the total frequency minus the noise frequency
    #use the first two days as the noises
    noise = np.zeros(24, np.float);
    for i in range(0,24):
        key = str(i);
        if key not in in_signal.keys():
            in_signal[key] = 0;
        if str(i+24) not in in_signal.keys():
            in_signal[str(i+24)] = 0;
        noise[i] = (in_signal[key] + in_signal[str(i+24)])/2.0

    out_signal = {};
    for time, freq in in_signal.iteritems():
        i = int(time);
        j = i%24;
        if (freq - noise[j]) < 0:
            continue;

        out_signal[time] = freq - noise[j];
    
    return out_signal;

def filterNoiseByKalman(in_signal):
    ndim = 1
    k = Kalman(ndim)    
    #mu_init=array([-0.37727])
    #cov_init=0.1*ones((ndim))
    #obs = random.normal(mu_init,cov_init,(ndim, nsteps))
    max_num = 0;
    for time, freq in in_signal.iteritems():
        if int(time) > max_num:
            max_num = int(time);
    max_num = max_num + 1;

    signal = np.zeros(max_num, np.float);
    for i in range(0, max_num):
        if str(i) in in_signal.keys():
            signal[i] = in_signal[str(i)];

    #obs = np.zeros(max_num));
    #for i in range(0, max_num):
    #    obs[:,i] = signal(i);

    for t in range(0, max_num):
        k.update(signal[t])

    return k.mu_hat_est 
