from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def change(tab, index):
    value = tab[index]
    tab[index] = tab[index + 1]
    tab[index + 1] = value


def tri(tab, start, end):
    r = 0
    for i in range(start, end + 1):
        if r == 0:
            for j in range(start, end + 1, 2):
                if j + 1 < end + 1 and tab[j] > tab[j + 1]:
                    change(tab, j)
            r = 1
        elif r == 1:
            for j in range(start + 1, end + 1, 2):
                if j + 1 < end + 1 and tab[j] > tab[j + 1]:
                    change(tab, j)
            r = 0
    return tab


def tri_min(tab1, tab2, start1, end1, start2, end2):
    te = list(tab1)
    i = start1
    s1 = start1
    s2 = start2

    while start1 <= end1 and start2 <= end2 and i <= end1:
        if tab1[s1] < tab2[s2]:
            te[i] = tab1[s1]
            s1 = s1 + 1
        else:
            te[i] = tab2[s2]
            s2 = s2 + 1
        i = i + 1
    return te


def tri_max(tab1, tab2, start1, end1, start2, end2):
    te = list(tab1)
    temp = list()
    i = end2 - start2
    for j in range(start2, end1 + 1):
        if j < start1:
            temp.append(tab2[j])
        else:
            temp.append(tab1[j])

    temp = tri(temp, 0, len(temp) - 1)

    for j in range(i, len(temp) - 1):
        te[start1] = temp[i + 1]
        i += 1
        start1 += 1
    return te


if __name__ == '__main__':
    table = [24, 7, 18, 23, 14, 16, 15, 20, 11, 12, 19, 5, 10, 25, 17, 3, 21, 1, 13, 8, 2, 9, 22, 6, 4]
    start = 0
    end = 0
    if size > len(table) - 1 or size < 2:
        print("-np ?  improper for table length Equal " + str(len(table)))
        exit()
    le = (len(table)) // (size - 1)

    if rank == 0:

        print("------------------------- P" + str(rank) + " -------------------------")
        print("table: " + str(table))
        for i in range(1, size):
            if end + le < len(table):
                if start == 0:
                    end += le - 1
                else:
                    end += le
            else:
                end = len(table)
            if i == size - 1 and end != len(table) - 1:
                end = len(table) - 1
            comm.send([table, start, end, size], dest=i, tag=11)
            print("send table to P" + str(i))
            if start == 0:
                start += le
            else:
                start += le

        for i in range(1, size):
            recv = comm.recv(source=i, tag=22)
            print("recv table from P" + str(i) + "--->" + str(recv[0]))
            for j in range(recv[1], recv[2] + 1):
                table[j] = recv[0][j]

        print("**** end ****")
        print(table)

    else:
        print("------------------------- P" + str(rank) + " -------------------------")
        dataRec = comm.recv(tag=11)
        print("change table index [" + str(dataRec[1]) + "..." + str(dataRec[2]) + "]")
        for i in range(0, dataRec[3]):
            if i == 0:
                dataRec[0] = tri(dataRec[0], dataRec[1], dataRec[2])
                print("step :tri table " + str(dataRec[0][dataRec[1]:dataRec[2]]))
            else:
                if rank % 2 == 0 and i % 2 == 0:
                    if rank + 1 < size:
                        comm.send([dataRec[0], dataRec[1], dataRec[2], size], dest=rank + 1, tag=11)
                        dataRec1 = comm.recv(tag=11, source=rank + 1)
                        dataRec[0] = tri_min(dataRec[0], dataRec1[0], dataRec[1], dataRec[2], dataRec1[1], dataRec1[2])
                        print("step :send and recv from P" + str(rank + 1) + " tri_min --> " + str(
                            dataRec[0][dataRec[1]:dataRec[2] + 1]))

                elif rank % 2 == 1 and i % 2 == 1:
                    if rank + 1 < size:
                        comm.send([dataRec[0], dataRec[1], dataRec[2], size], dest=rank + 1, tag=11)
                        dataRec1 = comm.recv(tag=11, source=rank + 1)
                        dataRec[0] = tri_min(dataRec[0], dataRec1[0], dataRec[1], dataRec[2], dataRec1[1], dataRec1[2])
                        print("step :send and recv from P" + str(rank + 1) + " tri_min --> " + str(
                            dataRec[0][dataRec[1]:dataRec[2] + 1]))

                else:
                    if rank - 1 > 0:
                        comm.send([dataRec[0], dataRec[1], dataRec[2], size], dest=rank - 1, tag=11)
                        dataRec1 = comm.recv(tag=11, source=rank - 1)
                        dataRec[0] = tri_max(dataRec[0], dataRec1[0], dataRec[1], dataRec[2], dataRec1[1], dataRec1[2])
                        print("step :send and recv from P" + str(rank - 1) + " tri_max --> " + str(
                            dataRec[0][dataRec[1]:dataRec[2] + 1]))

        print("*** end ***")
        print(dataRec[0][dataRec[1]:dataRec[2] + 1])
        comm.send([dataRec[0], dataRec[1], dataRec[2]], dest=0, tag=22)
        print("\n")
