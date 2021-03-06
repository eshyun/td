import torch
import torch.nn as nn
import torch.nn.functional as F


class Qnet(nn.Module):
    def __init__(self, layers = []): # first and last elements - unput shape and output shape
        super(Qnet, self).__init__()
        self.layer1  = nn.Linear(layers[0],layers[1])
        self.layer2 = nn.Linear(layers[1],layers[2])
        self.layer3 = nn.Linear(layers[2], layers[3])
   
    def forward(self, x):
        h = F.elu(self.layer1(x))
        h = F.elu(self.layer2(h))
        #h = F.tanh(self.layer3(h)) 
        h = self.layer3(h)
        return h
    
class DuelingQnet(nn.Module):
    def __init__(self, layers= []):
        super(DuelingQnet, self).__init__()
        self.layer1 = nn.Linear(layers[0],layers[1])
        self.layer2 = nn.Linear(layers[1],layers[2])
        '''layer for value state'''
        self.state = nn.Linear(layers[2], layers[3])
        ''' layer for advantage value '''
        self.adv = nn.Linear(layers[2], layers[3])
        
    def forward(self, x):
        h = F.elu(self.layer1(x))
        h = F.elu(self.layer2(h))
        #h = F.tanh(self.layer3(h)) 
        state = self.state(h)
        advantage = self.adv(h)
        return state, advantage
    
    
class DuelingLSTM(nn.Module):
    def __init__(self,  input_size, hidden_size, seq_length = 3, 
                 layers=1, batch_size=1, bidirectional=False, lin_layers = []):
        super(DuelingLSTM, self).__init__()
        directions = 2 if bidirectional else 1
        self._seq_length = seq_length
        self._batch_size = batch_size
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers = layers)
        self.h_0 = torch.randn((directions*layers, batch_size, hidden_size)) #initialize hidden state
        self.c_0 = torch.randn((directions*layers, batch_size, hidden_size)) #initialize cell state
        self.linear1 = nn.Linear(hidden_size*self._seq_length, lin_layers[0])
        ''' value state '''
        self.state = nn.Linear(lin_layers[0], lin_layers[1])
        ''' value advantage '''
        self.adv = nn.Linear(lin_layers[0], lin_layers[1])
    
    def reshape(self, x):
        return x.reshape(self._seq_length, self._batch_size, -1) # 3 - number of time periods, 
    #1 - batch_size, input_size - number of feature
    
    def forward(self, x):
        x = self.reshape(x)
        x, (self.h_0, self.c_0) = self.lstm(x, (self.h_0.detach(), self.c_0.detach()))
        x = x.view(-1)
        x = F.elu(self.linear1(x))
        state = self.state(x)
        adv = self.adv(x)
        return state, adv
