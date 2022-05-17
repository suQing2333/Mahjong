import time
import bisect
import mahjong_tools as mt
import copy



CardList = [
	0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19,               #万
	0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29,               #筒
	0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,               #条
	0x41, 0x44, 0x47, 0x4A,												#风,东南西北
	0x51, 0x54, 0x57,													#字,中发白
	]

handCardsList = []
handCardsMap = {}			# card:num
handCardsHuaMap = {}		# hua:{"num":total_num,value:num}
handCardsValueMap = {}		# value:{"num":total_num,hua:num}
handCardsCluster = []		# [{"cardList":[],"type":int}]
typeMap = {0:0,1:0,2:0}		# 如果一幅牌可以胡,那么一定没有type == 0,且有且只有一个type == 2

state = 0 #0,1,2

def StartInit():
	for card in CardList:
		handCardsMap[card] = 0
		hua = mt.getHua(card)
		value = mt.getValue(card)
		if not handCardsHuaMap.get(hua):
			handCardsHuaMap[hua] = {"num":0}
		if not handCardsHuaMap.get(hua).get(value):
			handCardsHuaMap[hua][value] = 0

		if not handCardsValueMap.get(value):
			handCardsValueMap[value] = {"num":0}
		if not handCardsValueMap.get(value).get(hua):
			handCardsValueMap[value][hua] = 0

def AddCard2HandCards(addCard):
	bisect.insort(handCardsList,addCard)
	card_hua = mt.getHua(addCard)
	card_value = mt.getValue(addCard)
	handCardsMap[addCard] += 1
	handCardsHuaMap[card_hua]["num"] += 1
	handCardsHuaMap[card_hua][card_value] += 1
	handCardsValueMap[card_value]["num"] += 1
	handCardsValueMap[card_value][card_hua] += 1
	ClusterType = ClusterAddCard(addCard)
	return ClusterType


def RemoveCard2HandCards(removeCard):
	handCardsList.remove(removeCard)
	card_hua = mt.getHua(removeCard)
	card_value = mt.getValue(removeCard)
	handCardsMap[removeCard] -= 1
	handCardsHuaMap[card_hua]["num"] -= 1
	handCardsHuaMap[card_hua][card_value] -= 1
	handCardsValueMap[card_value]["num"] -= 1
	handCardsValueMap[card_value][card_hua] -= 1
	ClusterType = ClusterRemoveCard(removeCard)
	return ClusterType

#插入进来的一张牌可能导致聚合融合
def ClusterAddCard(addCard):
	if len(handCardsCluster) == 0:
		handCardsCluster.append({"cardList":[addCard],"type":0})
		typeMap[0] += 1
		return 0
	fuse = []
	for i in range(0,len(handCardsCluster)):
		singleCluster = handCardsCluster[i]
		minDistance,minCard = GetMinHandCardsDistanceWithList(singleCluster.get("cardList",[]),addCard)
		if minDistance > 2:
			continue
		fuse.append(i)
	if len(fuse) == 0:
		handCardsCluster.append({"cardList":[addCard],"type":0})
		typeMap[0] += 1
	elif len(fuse) == 1:
		singleCluster = handCardsCluster[fuse[0]]
		bisect.insort(singleCluster.get("cardList",[]),addCard)
		typeMap[singleCluster.get("type")] -= 1
		threeNType = ConformThreeN(singleCluster.get("cardList",[]))
		singleCluster["type"] = threeNType
		typeMap[threeNType] += 1
		return threeNType
	# 当插入的牌与两个聚合的距离小于等于2时,则两个聚合会因为这张牌融合
	elif len(fuse) == 2:
		Cluster1 = handCardsCluster[fuse[0]]
		Cluster2 = handCardsCluster[fuse[1]]
		typeMap[Cluster1.get("type")] -= 1
		typeMap[Cluster2.get("type")] -= 1
		handCardsCluster.remove(Cluster1)
		handCardsCluster.remove(Cluster2)
		Cluster1CardList = Cluster1.get("cardList",[])
		Cluster2CardList = Cluster2.get("cardList",[])
		newCluster = {}
		cardList = []
		if Cluster1CardList[0] < Cluster2CardList[0]:
			cardList = Cluster1CardList+Cluster2CardList
		else:
			cardList = Cluster2CardList+Cluster1CardList
		bisect.insort(cardList,addCard)
		threeNType = ConformThreeN(cardList)
		newCluster = {"cardList":cardList,"type":threeNType}
		typeMap[threeNType] += 1
		handCardsCluster.append(newCluster)
		return threeNType
	else:
		print("需要聚合的聚合不可能超过两个")
	return 

# 移除的一张牌有可能导致聚合的分离
def ClusterRemoveCard(removeCard):
	if len(handCardsCluster) == 0:
		print("移除牌时聚合为空一定是有问题的")
		return
	# 找到元素所在聚合
	Cluster = {}
	for i in range(0,len(handCardsCluster)):
		singleCluster = handCardsCluster[i]
		if removeCard in singleCluster.get("cardList",[]):
			Cluster = singleCluster
			break
	if Cluster == {}:
		print("元素不存在")
		return
	handCardsCluster.remove(Cluster)
	typeMap[Cluster.get("type",0)] -= 1
	cardList = Cluster.get("cardList",[])
	removeIndex = cardList.index(removeCard)
	if removeIndex == 0 or removeIndex == len(cardList)-1:
		cardList.remove(removeCard)
		if len(cardList) == 0:
			return 0
		threeNType = ConformThreeN(cardList)
		Cluster["type"] = threeNType
		handCardsCluster.append(Cluster)
		typeMap[threeNType] += 1
		return threeNType
	# 移除一张牌导致聚合分离
	if cardList[removeIndex+1] - cardList[removeIndex-1] > 2:
		Cluster1CardList = cardList[:removeIndex]
		Cluster2CardList = cardList[removeIndex+1:]
		Cluster1Type = ConformThreeN(Cluster1CardList)
		Cluster2Type = ConformThreeN(Cluster2CardList)
		Cluster1 = {"cardList":Cluster1CardList,"type":Cluster1Type}
		Cluster2 = {"cardList":Cluster2CardList,"type":Cluster2Type}
		typeMap[Cluster1Type] += 1
		typeMap[Cluster2Type] += 1
		handCardsCluster.append(Cluster1)
		handCardsCluster.append(Cluster2)
		if Cluster1Type >= 1 and Cluster2Type >= 1:
			return 1
		else:
			return 0
	else:
		cardList.remove(removeCard)
		if len(cardList) == 0:
			return
		threeNType = ConformThreeN(cardList)
		Cluster["type"] = threeNType
		handCardsCluster.append(Cluster)
		typeMap[threeNType] += 1
		return threeNType
	return 0

# 当所有聚合中不存在未成牌的聚合且有且只有一个3n+2的聚合
def IsHu():
	if typeMap[0] == 0 and typeMap[2] == 1:
		return True
	return False

# 打出某张牌听牌
# 一定存在  typeMap[0] <= 2  存在三种情况
def TingInfo():
	tingInfo = {}
	checkMap = {}
	if typeMap[0] > 2:
		return tingInfo
	#当typeMap[0] == 1 此时玩家还有一个聚合没有成牌,所以能出的牌一定在这个聚合内,能胡的牌也一定是这个聚合[min-1,max+1]的范围
	elif typeMap[0] == 1:
		Cluster = {}
		for singleCluster in handCardsCluster:
			if singleCluster.get("type") == 0:
				Cluster = copy.deepcopy(singleCluster)
				break
		cardList = Cluster.get("cardList",[])
		for card in cardList:
			if checkMap.get(card) == 1:
				continue
			else:
				checkMap[card] = 1
			tingInfo[card] = []
			if len(cardList) >= 1:
				del tingInfo[card]
				return tingInfo
			RemoveCard2HandCards(card)
			cardList.remove(card)
			minCard = cardList[0]-1 if cardList[0]-1 in CardList else cardList[0]
			maxCard = cardList[len(cardList)-1]+1 if cardList[len(cardList)]+1 in CardList else cardList[len(cardList)]
			for addCard in range(minCard,maxCard+1):
				AddCard2HandCards(addCard)
				if IsHu():
					tingInfo[card].append(addCard)
				RemoveCard2HandCards(addCard)
			AddCard2HandCards(card)
			bisect.insort(cardList,card)
			if len(tingInfo[cardListLen1[0]]) == 0:
				del tingInfo[card]
	#当typeMap[0] == 2 
	# 则有两种情况: 1打出聚合1的牌,胡牌范围为聚合2[min-1,max+1] 2玩家打出聚合2的牌,胡牌范围为聚合1[min-1,max+1]
	# 并且两种情况互斥(大概)
	# 其实两种情况可以合并为一种,即为打出聚合中的一张牌,满足type >= 1,todo
	elif typeMap[0] == 2:
		Cluster1 = {}
		Cluster2 = {}
		for singleCluster in handCardsCluster:
			if singleCluster.get("type") == 0 :
				if Cluster1 == {}:
					Cluster1 = copy.deepcopy(singleCluster)
				else:
					Cluster2 = copy.deepcopy(singleCluster)
		# 先处理聚合1
		cardList1 = Cluster1.get("cardList")
		cardList2 = Cluster2.get("cardList")
		for card in cardList1:
			if checkMap.get(card) == 1:
				continue
			else:
				checkMap[card] = 1
			tingInfo[card] = []
			RemoveCard2HandCards(card)
			cardList1.remove(card)
			minCard = cardList2[0]-1 if cardList2[0]-1 in CardList else cardList2[0]
			maxCard = cardList2[len(cardList2)-1]+1 if cardList2[len(cardList2)-1]+1 in CardList else cardList2[len(cardList2)-1]
			for addCard in range(minCard,maxCard+1):
				AddCard2HandCards(addCard)
				if IsHu():
					tingInfo[card].append(addCard)
				RemoveCard2HandCards(addCard)
			AddCard2HandCards(card)
			bisect.insort(cardList1,card)
			if len(tingInfo[card]) == 0:
				del tingInfo[card]
		for card in cardList2:
			if checkMap.get(card) == 1:
				continue
			else:
				checkMap[card] = 1
			tingInfo[card] = []
			RemoveCard2HandCards(card)
			cardList2.remove(card)
			minCard = cardList1[0]-1 if cardList1[0]-1 in CardList else cardList1[0]
			maxCard = cardList1[len(cardList1)-1]+1 if cardList1[len(cardList1)-1]+1 in CardList else cardList1[len(cardList1)-1]
			for addCard in range(minCard,maxCard+1):
				AddCard2HandCards(addCard)
				if IsHu():
					tingInfo[card].append(addCard)
				RemoveCard2HandCards(addCard)
			AddCard2HandCards(card)
			bisect.insort(cardList2,card)
			if len(tingInfo[card]) == 0:
				del tingInfo[card]

	# 当typeMap[0] == 0 时,其实这个时候玩家已经胡牌,能出的牌为全手牌
	# 但是也有限制,因为当前情况下聚合已经全部成牌,所以想要打一张听牌一定是破坏当前已成牌的聚合
	# 所以打出一张牌,胡牌范围一定是当前聚合[min-1,max+1]
	elif typeMap[0] == 0:
		#todo
		pass
	return tingInfo

# 获取最小牌距
def GetMinHandCardsDistanceWithMap(cardMap,card):
	minDistance = -1
	minCard = -1
	for singleCard,num in cardMap.items():
		if minDistance == -1:
			minDistance = abs(singleCard-card)
			minCard = card
		elif abs(singleCard-card) < minDistance :
			minDistance = abs(singleCard-card)
			minCard = card
	return minDistance,minCard

def GetMinHandCardsDistanceWithList(cardList,card):
	tmpMap = mt.CardList2Map(cardList)
	return GetMinHandCardsDistanceWithMap(tmpMap,card)

# 检测一个聚合是否满足3n或者3n+2
# 0 不满足 1 满足3n  2 满足3n+2
def ConformThreeN(arr):
	cardList = copy.deepcopy(arr)
	cardMap = mt.CardList2Map(cardList)
	flag = True
	if len(cardList) <= 1:
		return 0
	# 可能存在3n+2关系
	# 3n+2一定会存在某个值出现次数大于等于2
	# 可能存在多种将的情况
	if len(cardList) % 3 == 2:
		for card,num in cardMap.items():
			# 可作将
			if num < 2:
				continue
			tmpList = copy.deepcopy(cardList)
			tmpMap = copy.deepcopy(cardMap)
			tmpList.remove(card)
			tmpList.remove(card)
			tmpMap[card] -= 2
			flag = mt.ThreeN(tmpList,tmpMap)
			if flag:
				return 2
			
	if len(cardList) % 3 == 0:
		tmpList = copy.deepcopy(cardList)
		tmpMap = copy.deepcopy(cardMap)
		flag = mt.ThreeN(tmpList,tmpMap)
		if flag:
			return 1
	return 0

def test(arr):
	for i in arr:
		AddCard2HandCards(i)
		print(handCardsCluster,"   ",typeMap)
		print(TingInfo())


StartInit()
arr = [0x11,0x11,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x19,0x19,0x21]
test(arr)