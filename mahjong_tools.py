def getValue(card):
	return card&0x0F

def getHua(card):
	return int((card&0xF0)/16)

def CardList2Map(cardList):
	cardMap = {}
	for card in cardList:
		if cardMap.get(card,-1) == -1:
			cardMap[card] = 1
		else:
			cardMap[card] += 1
	return cardMap

#3n 要组成3n,不是顺子就是刻子
def ThreeN(cardList,cardMap):
	while len(cardList) > 0:
		card = cardList[0]
		num = cardMap[card]
		if num <= 2:
			if cardMap.get(card+1) and  cardMap[card+1] >= num and cardMap.get(card+2) and cardMap[card+2] >= num:
				for i in range(0,num):
					cardList.remove(card)
					cardMap[card] -= 1
					cardList.remove(card+1)
					cardMap[card+1] -= 1
					cardList.remove(card+2)
					cardMap[card+2] -= 1
			else:
				return False
		# 同后面组成顺 或者自己组成刻
		if num == 3:
			if cardMap.get(card+1) and  cardMap[card+1] >= num and cardMap.get(card+2) and cardMap[card+2] >= num:
				for i in range(0,num):
					cardList.remove(card)
					cardMap[card] -= 1
					cardList.remove(card+1)
					cardMap[card+1] -= 1
					cardList.remove(card+2)
					cardMap[card+2] -= 1
			else:
				for i in range(0,3):
					cardList.remove(card)
		if num == 4:
			minNum = 0
			minNum = max(num,cardMap[card+1],cardMap[card+2])
			if (minNum == 4 or minNum == 1) and cardMap.get(card+1) and  cardMap[card+1] >= minNum and cardMap.get(card+2) and cardMap[card+2] >= minNum:
				for i in range(0,minNum):
					cardList.remove(card)
					cardMap[card] -= 1
					cardList.remove(card+1)
					cardMap[card+1] -= 1
					cardList.remove(card+2)
					cardMap[card+2] -= 1
			else:
				return False
	return True