"""
Copyright 2019 Baris Akgun

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of
conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or other materials provided
with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to
endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Most importantly, this software is provided for educational purposes and should not be used for
anything else.

AUTHORS: Baris Akgun

"""

import util, copy, math, random
import baseAgents, policies

"""
This agent is given to you as an example
"""
class PolicyEvaluationAgent(baseAgents.BaseDpAgent):
    """
    Agent that runs the policy evaluation algorithm.
    """
    def __init__(self, mdp, env, discount = 0.9, policy=None, errorThreshold = 0.001, maxIters=1000):
        """
        mdp: The underlying Markov Decision Process 
        env: Environment of the agent
        discount: The discount factor. Should actually be part of the mdp but this implementation makes the agent select it
        policy: The (initial or to be evaluated) policy of the agent
        errorThreshold: The approximation error threshold for value prediction. 
        maxIters: The maximum allowed iterations for policy evaluation. 
        """
        super().__init__(mdp, env, discount, policy)
        self.errorThreshold = errorThreshold
        self.maxIters = maxIters
        
        if policy is None:
            self.policy = policies.RandomPolicy(self, returnProbabilities = True)

    def run(self):
        """
        The function that we call to calculate the values. 
        Returns the number of iterations
        """
        thresh = self.errorThreshold*(1-self.discount)/self.discount
        for iters in range(self.maxIters):
            if(self._iter() < thresh):
                break
        return iters
        
    def _iter(self):
        """
        A single policy iteration evaluation. 
        Returns the maximum difference between previous values and current values
        """
        delta = -math.inf
        V = copy.deepcopy(self.values)
        states = self.mdp.getStates()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            val = 0
            actions = self.mdp.getPossibleActions(state)
            for action in actions:
                actionProbs = self.policy.policyProbs(state)
                val += actionProbs[action]*self._getQValue(state, action, V)
            self.values[state] = val
            delta = max(abs(V[state]-val),delta)
        return delta

    def getQValues(self):
        for state in self.mdp.getStates():
            for action in self.mdp.getPossibleActions(state):
                self.qvalues[(state,action)] = self.getQValue(state,action)
        return self.qvalues

    def _getQValue(self, state, action, V):
        val = 0
        for actPr in self.mdp.getTransitionStatesAndProbs(state, action):
            nextState = actPr[0]
            pr = actPr[1]
            if pr == 0:
                continue
            val += pr*(self.mdp.getReward(state, action, nextState) + self.discount*V[nextState])
        return val

    def getQValue(self, state, action):
        return self._getQValue(state, action, self.values)

class QValueIterationAgent(baseAgents.BaseDpAgent):
    """
    Agent that runs the q-value iteration algorithm
    """
    def __init__(self, mdp, env, discount = 0.9, errorThreshold = 0.001, maxIters=1000):
        """
        mdp: The underlying Markov Decision Process 
        env: Environment of the agent
        discount: The discount factor. Should actually be part of the mdp but this implementation makes the agent select it.
        policy: The (initial or to be evaluated) policy of the agent
        errorThreshold: The approximation error threshold for value prediction. 
        maxIters: The maximum allowed iterations for policy evaluation. 
        """
        super().__init__(mdp,env,discount)
        self.errorThreshold = errorThreshold*(1-self.discount)/self.discount
        self.maxIters = maxIters
        
        self.policy = policies.PolicyFromQValues(self)

        """
        You can add your own fields
        Recall that we initialize the q-values to all zeros already
        """
        
    """
    You can add your own functions
    """
    

    def run(self):
       # util.raiseNotDefined()
        
        """
        Comment out the previous line and write your code here.
        You need to implement q-value iteration.
        After this method is run, self.qvalues must be filled with the correct q-values.
        Do not forget to set the convergence criteria using both the maxIters and the self.errorThreshold!
        Do not forget to return the number of iterations
        Feel free to add new methods
        Simplifying Hint: max(Q(s,a)) = V(s) = self.getValue(s), as long as the self.policy returns the greedy action which it does already
        
        return the number of iterations!
        """
        """
        The function that we call to calculate the qalues. 
        Returns the number of iterations
        """
        thresh = self.errorThreshold*(1-self.discount)/self.discount
        for iters in range(self.maxIters):
            if(self._iter() < thresh):
                break
        return iters
    
    def _iter(self):
        """
        A single policy iteration evaluation. 
        Returns the maximum difference between previous values and current values
        """
        delta = -math.inf
        Q = copy.deepcopy(self.qvalues)
        states = self.mdp.getStates()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            for action in actions:
                qval = self._getQValue(state, action)
                self.qvalues[(state, action)] = qval
            delta = max(abs(Q[(state, action)]-qval),delta)
        return delta
    
    def _getQValue(self, state, action):
        val = 0
        for actPr in self.mdp.getTransitionStatesAndProbs(state, action):
            nextState = actPr[0]
            pr = actPr[1]
            if pr == 0:
                continue
            val += pr*(self.mdp.getReward(state, action, nextState) + self.discount*self.getValue(nextState))
        return val

    def getValue(self, state):
        act = self.policy(state)
        val = self.qvalues[(state, act)]
        return val

    def getValues(self):
        for state in self.mdp.getStates():
            self.values[state] = self.getValue(state)
        return self.values

class PolicyIterationAgent(PolicyEvaluationAgent):
    """
    Agent that runs the policy iteration algorithm. 
    It extends the PolicyEvaluationAgent in case you want to use that functionality.
    """
    def __init__(self, mdp, env, initialPolicy=None, discount = 0.9):
        """
        mdp: The underlying Markov Decision Process 
        env: Environment of the agent
        discount: The discount factor. Should actually be part of the mdp but this implementation makes the agent select it
        policy: The (initial or to be evaluated) policy of the agent
        errorThreshold: The approximation error threshold for value prediction. 
        maxIters: The maximum allowed iterations for policy evaluation. 
        """
        super().__init__(mdp, env, discount, initialPolicy, 0.01,10)
        
        """
        You can add your own fields
        """
        self.mdp = mdp
        self.env = env
        self.discount = discount

    """
    You can add your own functions
    """

    def run(self):
        #util.raiseNotDefined()
        """
        Comment out the previous line and write your code here.
        You need to implement policy iteration.
        After this method is run, self.getPolicy must return the optimal policy
        Feel free to add new methods
        Do not forget to return the number of iterations
        Hints:
        - You need to deepcopy policies at each iteration
        - super().run() would take care of the evaluation for you! However, this maybe inefficient if error threshold is low.
        - You need to implement something to get the best action from the values (policy extraction)
        - You need to implement something that compares two policies
        - You can assume that you will always be given a TabularPolicy object (note that you need to have a "newPolicy" as well, 
          e.g.  newPolicy = policies.TabularPolicy(self))
          
        return the number of iterations!
        """
 
        init_policy_Table = util.Counter()
        states = self.mdp.getStates()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            init_policy_Table[state] = random.choice(actions)
        self.policy = policies.TabularPolicy(self, policyTable=init_policy_Table)
        
        for iters in range(self.maxIters):
            self.evaluator = PolicyEvaluationAgent(self.mdp, self.env, policy=self.policy)
            self.evaluator.run()
            self.new_policy = self.get_policy_from_values(self.evaluator)
            self.values = self.evaluator.getValues()
            if self.policies_equal(self.policy, self.new_policy):
                break
            self.policy = self.new_policy
        return iters
    
    def get_policy_from_values(self, evaluator):
        policyTable = util.Counter()
        states = self.mdp.getStates()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            action_selector = util.Counter()
            for action in actions:
                action_selector[action] =  evaluator._getQValue(state, action, evaluator.values)
            best_action = self.argmax(action_selector)
            policyTable[state] = best_action
        return policies.TabularPolicy(self, policyTable=policyTable)
    
    def argmax(self, dict):
        #custom argmax since Counter.argMax and Counter.sortedKeys is broken
        return max(dict, key=dict.get)
    
    def policies_equal(self, old_policy, new_policy):
        return old_policy.policyTable == new_policy.policyTable
            

