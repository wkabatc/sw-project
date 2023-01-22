import string

def lev(word1, word2):
    for punct in string.punctuation:
        word1 = word1.replace(punct, ' ').lower().strip()
        word2 = word2.replace(punct, ' ').lower().strip()
        
    matrix = []
    for i in range(len(word2) + 1):
        row = []
        row.append(i)
        matrix.append(row)
    for j in range(len(word1)):
        matrix[0].append(j+1)

    rowIterator = 1
    columnIterator = 1
    for c in word2:
        rowIterator = 1
        for c2 in word1:
            result1 = matrix[columnIterator - 1][rowIterator] + 1
            result2 = matrix[columnIterator - 1][rowIterator - 1] + 1
            if c == c2:
                result2 = result2 - 1
            result3 = matrix[columnIterator][rowIterator - 1] + 1
            result = min(result1, result2, result3)
            matrix[columnIterator].append(result)
            rowIterator = rowIterator + 1
        columnIterator = columnIterator + 1

    levLength = matrix[len(matrix)-1][len(word1)]
    
    return levLength