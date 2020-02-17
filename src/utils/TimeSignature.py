import math
def get_time_signature(recurrence_matrix, candidates):
    sms = []
    for bar_len in candidates:
        diagonals = []
        for i in range(bar_len, recurrence_matrix.shape[0], bar_len):
            ii = i
            jj = 0
            diag = []
            while ii < recurrence_matrix.shape[0] and jj < recurrence_matrix.shape[1]:
                diag += [recurrence_matrix[ii, jj]**2]
                ii += 1
                jj += 1
            diagonals += [diag]
        full_sets = []
        partials = [[]]
        for diag in diagonals:
            i = 0
            while i < len(diag):
                s = []
                for _ in range(bar_len):
                    s += [diag[i]]
                    i += 1
                    if i >= len(diag): break
                if len(s) == bar_len: full_sets += [s]
                else: partials += [s]
        sum_scs = 0
        for s in full_sets:
            sum_scs += math.sqrt(sum(s) / bar_len)
        sum_sis = 0
        for s in partials[1:]:
            sum_sis += math.sqrt(sum(s) / len(s))
        sm = (bar_len*sum_scs + len(partials[0])*sum_sis) / \
            (bar_len * len(full_sets) + len(partials[0]) * len(partials))
        sms += [sm]
    return sms