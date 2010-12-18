#! /user/bin/env python
#user provides handle and corresponding tweet
#persistantly check for retweets of the provided input
#follow each retweeter and rank them accordingly

import tweepy
import getpass
import os.path
import json
import pickle
import sys
import decimal


class Node:
    def __init__(self, user, rank, lvl, ts, twid, parent_twid):
        self.user = user
        self.rank = rank
        self.lvl = lvl
        self.ts = ts
        self.twid = twid
        self.rtusr = parent_twid #parent twid, this is a retweet of rtuser
        
class parentNode:
    def __init__(self, parent, parent_twid, twid):
        self.parent = parent
        self.parent_twid = parent_twid
        self.twid = twid


#depreciated function, will not work after Aug 16
def authenticate(usr='0', pswd='0'):
    if usr == '0':
        usr = raw_input("twitter username: ")
        pswd = getpass.getpass("password: ")
    auth = tweepy.BasicAuthHandler(usr, pswd)
    api = tweepy.API(auth)
    return api


#authenticate using OAuth
def Oauthenticate():
    auth = tweepy.OAuthHandler('XSlYVMJ9ebCXOfdOPolgDg', 'RQdQxOnPFRqKogfVqL0JdpGwadXZ6XawtXn7QpcQ')
    
    try:
        redirect_url = auth.get_authorization_url()
        print 'Please visit the following URL and allow access to Reverb.it:'
        print redirect_url
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'

    verifier = raw_input('Please enter the pin code: ')
    
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'


    #save tokens to file
    filename = 'token.txt'
    FILE = open(filename, 'w')
    FILE.write(auth.access_token.key)
    FILE.write(auth.access_token.secret)
    FILE.close()
    
    api = tweepy.API(auth)
    return api

def SaveAndPickle(tree):
    filename = 'jsonRanks.txt'
    FILE = open(filename, 'w')
    
    pickle.dump(tree, FILE)


#creates a retweet chian tree, if a retweet is not of a another retweet, it is assumed to be the direct retweet of the orignal tweet
def get_followers(tweetID, auth):
    rt = auth.retweets(tweetID)
    twt = auth.get_status(tweetID) #get the original tweet

    rt.append(twt)
    rt.reverse()    #reverse the order of the list, this will return list in order of tweet creation time

    tree = [] #start the tree
    lvl_users = [] #start list for users in this level of tree
    nxt_lvl = [] #users in the next level

    lvl_idx = 0

    while(len(rt) > 0):
        del lvl_users[:]    #make sure lvl_users is cleared

        if(lvl_idx != 0):
            lvl_idx = 1
            
        node = Node(rt[0].user, float(0), lvl_idx, rt[0].created_at, rt[0].id, twt.id)
        tree.append(node)
        lvl_users.append(node)  #place first element in rt into lvl_users since rt is ts sorted,
                                #it cannot be a retwet of any rts that come after it in the array
        
        rt.pop(0)            #remove the top in rt
        
        loop = True

        while (loop):
            while (len(lvl_users) > 0):
                #get followers
                try:
                    followers = auth.followers_ids(lvl_users[0].user.screen_name)
                except tweepy.error.TweepError:
                    print 'request to twitter failed'
                    return
                    
                lvl_idx = lvl_idx + 1 #increase level value

                #match followers with users in rt
                for r in rt:
                    for f in followers:
                        if(r.user.id == f):
                            #create a node in tree and node in next_lvl
                            node = Node(r.user, float(0), lvl_idx, r.created_at, r.id, lvl_users[0].twid)

                            #insert node into tree and nxt_lvl
                            tree.append(node)
                            nxt_lvl.append(node)

                            #delete matched user from rt, shortens rt list, for faster iteration next time
                            rt.remove(r)
                        

                #delete top from lvl_users
                lvl_users.pop(0)

            if(len(nxt_lvl) == 0):
                loop = False

            del lvl_users[:]    #delete lvl_users list
            lvl_users = list(nxt_lvl) #copy nxt_lvl list int lvl_users
            del nxt_lvl[:] #clear next level list
            

    return tree
        
        

def calcRank(tree):

    topnode = tree[0]           #get the top node
    treeReverse = tree                  #copy tree
    treeReverse.reverse()               #reverse the order of tree
    
    for nodes in treeReverse:          #moving down tree list in reverse order (tree is reverse of topTree)

        current_node = nodes
        temp = current_node

        while(temp.twid != topnode.twid):
        
            #find index of parent node in topTree
            for prnt in tree:
                if(temp.rtusr == prnt.twid):
                    idx = tree.index(prnt)          #get index of parent node in top tree
                    break                           #parent idx found no need to continue

            lvl_diff = current_node.lvl - tree[idx].lvl      #find the number of levels in between
            tree[idx].rank = tree[idx].rank + (1.0/lvl_diff) #increase rank

            temp = tree[idx]
    return tree


    
def main():
    if(len(sys.argv) <= 1):
        print 'tweet id not provided, user must provide a tweet id'
        return

    try:
        stripped = str(int(sys.argv[1]))
    except:
        print 'not a valid tweet id, must be an intger value'
        return
        
    if(os.path.isfile('token.txt')):
       f = open('token.txt', 'r')
       key = f.readline()
       secret = f.readline()
       auth = tweepy.OAuthHandler('XSlYVMJ9ebCXOfdOPolgDg', 'RQdQxOnPFRqKogfVqL0JdpGwadXZ6XawtXn7QpcQ')
       auth.set_access_token(key, secret)
       api = tweepy.API(auth)
       
    else:
        api = Oauthenticate()


    try:
        tree = get_followers(sys.argv[1], api)
        
    except tweepy.TweepError:
        print 'token invalid'
        api = Oauthenticate()
        tree = get_followers(sys.argv[1], api)
        calcRank(tree)

    
    SaveAndPickle(tree)


        
if __name__ == "__main__":
    main()
