#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 11:54:10 2022

@author: mariaolaru
"""

from pickle import TRUE


def get_next_trial_params(df_trials, max_amp, STIM_AMP_INTERVAL, STIM_FREQ_INTERVAL, init_stim_freq, entrain_trial_kernel):
    #Place holder algorithm for now
    t = df_trials['entrained'].count()-1

    curr_max_amp = get_curr_max_amp(max_amp, init_stim_freq, df_trials['stim_freq'][t])

    amp_curr = df_trials['stim_amp'][t]
    freq_curr = df_trials['stim_freq'][t]
    entrain_curr = df_trials['entrained'][t]

    if t == 0:
        amp_next = amp_curr - STIM_AMP_INTERVAL #begin traveling down in amplitude       
        freq_next = freq_curr
        return [amp_next, freq_next, t+1]

    amp_prev = df_trials['stim_amp'][t-1]
    freq_prev = df_trials['stim_freq'][t-1]
    entrain_prev = df_trials['entrained'][t-1]

    travel_down = amp_curr < amp_prev
    travel_up = amp_curr > amp_prev
    travel_left = freq_curr < freq_prev
    travel_right = freq_curr > freq_prev

    travel_opts = [travel_down, travel_up, travel_left, travel_right]

    if entrain_prev == False:       
            amp_next = amp_curr - STIM_AMP_INTERVAL
            freq_next = freq_curr            
    elif entrain_prev == True:
            if entrain_curr == False:
                if travel_opts[0] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp'] + STIM_AMP_INTERVAL
                    freq_next = freq_curr
                elif travel_opts[1] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp']
                    freq_next = df_trials.loc[entrain_trial_kernel, 'stim_freq'] - STIM_FREQ_INTERVAL
                    if(redundant_settings(df_trials, amp_next, freq_next)):
                        travel_opts[3] = True ##CONTINUE WORKING ON THIS TOMORROW
                        amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp'] - STIM_AMP_INTERVAL
                        freq_next = df_trials.loc[entrain_trial_kernel, 'stim_freq'] - STIM_FREQ_INTERVAL*2
                        curr_kernel = t+1                                            
                elif travel_opts[2] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp']
                    freq_next = df_trials.loc[entrain_trial_kernel, 'stim_freq'] + STIM_FREQ_INTERVAL
                elif travel_opts[3] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp'] - STIM_AMP_INTERVAL
                    freq_next = df_trials.loc[entrain_trial_kernel, 'stim_freq'] - STIM_FREQ_INTERVAL*2
                    curr_kernel = t+1                    
            elif entrain_curr == True:
                if travel_opts[0] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp'] - STIM_AMP_INTERVAL
                    freq_next = freq_curr
                elif travel_opts[1] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp'] + STIM_AMP_INTERVAL
                    freq_next = freq_curr                    
                elif travel_opts[2] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp']
                    freq_next = freq_curr - STIM_FREQ_INTERVAL
                elif travel_opts[2] == True:
                    amp_next = df_trials.loc[entrain_trial_kernel, 'stim_amp']
                    freq_next = freq_curr + STIM_FREQ_INTERVAL                            

    #[amp_next, freq_next] = redundant_settings(df_trials, amp_next, freq_next)
    
    return [round(amp_next, 1), round(freq_next, 4), entrain_trial_kernel]

def get_curr_max_amp(max_amp, init_stim_freq, curr_stim_freq):
    FREQ_INTERVAL = 2.5
    AMP_INTERVAL = 0.1

    d_freq = abs(init_stim_freq - curr_stim_freq)
    num_amp_steps = d_freq/FREQ_INTERVAL
    curr_max_amp = max_amp - (num_amp_steps*AMP_INTERVAL)
    
    return curr_max_amp

def redundant_settings(df_trials, amp_next, freq_next):
    redund = False
    amp_redund = False
    freq_redund = False
    
    if (df_trials['stim_amp'] == amp_next).any():
        amp_redund = True
    if (df_trials['stim_freq'] == freq_next).any():
        freq_redund = True
    if ((amp_redund == True) & (freq_redund == True)):
        redund = True
     
    return redund



def find_bottom(stim_amp, stim_freq, trial_entrained, bottom_boundary, freq_bounds_exclusive, prev_entrained, clinical_freq, bottom_finished):
    
    freq_step = -10
    if len(freq_bounds_exclusive) == 1:
        freq_step = 10

    if trial_entrained:
        if prev_entrained[0] or len(prev_entrained) == 0:
            amp_next = stim_amp - 0.1
            freq_next = stim_freq
        else:
            bottom_boundary[stim_freq] = stim_amp
            amp_next = stim_amp
            freq_next = stim_freq + freq_step
        
        prev_entrained[0] = True
   
    else:
        if prev_entrained[0]:
            bottom_boundary[stim_freq] = stim_amp + 0.1
            freq_next = stim_freq + freq_step
            amp_next = stim_amp + 0.1
            prev_entrained[0] = False
        else:
            freq_next = stim_freq
            amp_next = stim_amp + 0.1
            
            if amp_next == 6.1:
                freq_bounds_exclusive.append(stim_freq)

                if len(freq_bounds_exclusive) == 1:
                    amp_next = bottom_boundary[clinical_freq]
                    freq_next = clinical_freq + 10
                    prev_entrained[0] = True
                    return [freq_next, amp_next]
                else:
                    bottom_finished[0] = True
                    freq_next = stim_freq-10
                    amp_next = stim_amp
                    
        prev_entrained[0] = False

    return [freq_next, amp_next]


def find_top(stim_amp, stim_freq, trial_entrained, bottom_boundary, top_boundary, prev_entrained):
  
    if trial_entrained:

        if stim_freq == list(bottom_boundary)[len(bottom_boundary)]:
            top_boundary[stim_freq] = stim_amp
            amp_next = stim_amp
            freq_next = stim_freq-10
            prev_entrained[0] = True

        if prev_entrained[0]:
            amp_next = stim_amp + 0.1
            freq_next = stim_freq
            prev_entrained[0] = True
            if amp_next == 6.1:
                amp_next = stim_amp
                freq_next = stim_freq-10
                if freq_next < list(bottom_boundary)[0]:
                    top_finished = True
        else:
            top_boundary[stim_freq] = stim_amp
            amp_next = stim_amp
            freq_next = stim_freq-10
            prev_entrained[0] = True
    else:
        if prev_entrained[0]:
            top_boundary[stim_freq] = stim_amp - 0.1
            amp_next = stim_amp
            freq_next = stim_freq - 10
            prev_entrained[0] = False
        else:
            amp_next = stim_amp - 0.1
            freq_next = stim_freq
            prev_entrained[0] = False


    return [freq_next, amp_next]


def generate_next_params(stim_amp, stim_freq, trial_entrained, bottom_boundary, top_boundary, freq_bounds_exclusive, prev_entrained, clinical_freq, bottom_finished):
    if bottom_finished:
        [freq_next, amp_next] = find_top(stim_amp, stim_freq, trial_entrained, bottom_boundary, top_boundary, prev_entrained)
    else:
        [freq_next, amp_next] = find_bottom(stim_amp, stim_freq, trial_entrained, bottom_boundary, freq_bounds_exclusive, prev_entrained, clinical_freq, bottom_finished) 

    return [freq_next, amp_next]
