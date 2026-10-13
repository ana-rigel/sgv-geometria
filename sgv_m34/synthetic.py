"""S1-S5 synthetic feature-power experiments. Not an end-to-end particle mechanism."""
import numpy as np
from .core import fit_and_score,N_NODES
def generate_episodes(scenario,seed=20261013,n_episodes=60,episode_size=56):
    if scenario not in ('S1_markov','S2_moments','S3_circulation',
                        'S4_geometry','S5_redundant'):raise ValueError('scenario')
    rng=np.random.default_rng(seed);out=[]
    for j in range(n_episodes):
        current=rng.integers(0,4,size=episode_size)
        base=np.column_stack((np.eye(N_NODES)[current],
                              rng.normal(size=(episode_size,17))))
        conv=rng.normal(size=15);geom=rng.normal(size=8);geom[-1]=0
        labels=[]
        for st in current:
            logits=np.full(4,.1)
            if scenario in ('S1_markov','S3_circulation'):
                logits[(st+1)%4]+=2.8 if scenario=='S3_circulation' else 2.1
            elif scenario in ('S2_moments','S5_redundant'):
                logits[0]+=2.7*conv[0];logits[1]-=2.7*conv[0]
            elif scenario=='S4_geometry':
                logits[0]+=3.5*geom[0];logits[1]-=3.5*geom[0]
            if scenario=='S5_redundant':geom[0]=conv[0]
            p=np.exp(logits-logits.max());p/=p.sum()
            labels.append(rng.choice(4,p=p))
        out.append({'episode':j,'X_base':base,'conventional':conv,
                    'geometry':geom,'y':np.array(labels)})
    return out

def run_synthetic(seed=20261013,n_episodes=60):
    result={}
    for i,name in enumerate(('S1_markov','S2_moments','S3_circulation',
                             'S4_geometry','S5_redundant')):
        r=fit_and_score(generate_episodes(name,seed+100*i,n_episodes))
        result[name]={'losses':r['losses'],'test_differences_nats':
                      r['test_differences_nats'],
                      'n_test_episodes':len(r['splits']['test'])}
    return {'status':'synthetic feature-power, NOT confirmatory',
            'scenarios':result}
