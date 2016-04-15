
# coding: utf-8

# In[1]:

from pyciss.io import RingCube, PathManager


# In[2]:

pm = PathManager("N1591682340") 


# # meta development

# In[5]:

import pkg_resources as pr


# In[11]:

with pr.resource_stream('pyciss', 'data/ring_resonances.csv') as f:
    resonances = pd.read_csv(f)
resonances.head()


# In[13]:

resonances.sort_values(by='Resonance (km)',ascending=False)


# In[3]:

from pyciss.meta import meta_df


# In[4]:

meta_df.head()


# In[3]:

cube = RingCube(pm.cal_cub)


# In[5]:

cube.is_lit


# In[14]:

from pyciss.meta import meta2500m as meta


# In[15]:

cube.meta.ring_geom


# In[16]:

meta[meta.id==cube.pm._id]


# In[ ]:


