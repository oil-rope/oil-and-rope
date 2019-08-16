import random


def all(message):
    if message.content.startswith('..'):
        if message.content[2] == 'd' or message.content[2] == 'D' or message.content[2].isdigit():
            channel = message.channel

            contexto = message.content

            lenght = len(contexto)
            result = []
            adding = []

            if '+' in contexto:
                half = contexto.find('+')
                adding = contexto[half:]
                contexto = contexto[0:half]
                add = True
            else:
                add = False

            mode_n = True
            mode_d = False
            aux = 0
            ndice = 0
            szdice = 0

            if contexto[2] == 'd' or contexto[2] == 'D':
                ndice = 1

            for i in range(len(contexto)):
                if contexto[i] == 'd' or contexto[i] == 'D':
                    mode_n = False
                    mode_d = True
                elif contexto[i].isdigit():
                    aux += int(contexto[i])
                    if contexto[i-1].isdigit():
                        if mode_n:
                            ndice *= 10
                            ndice += aux
                        elif mode_d:
                            szdice *= 10
                            szdice += aux
                    else:
                        if mode_n:
                            ndice += aux
                        elif mode_d:
                            szdice += aux

                    aux = 0

            symbol = True
            aux = 0
            bonus = []
            j = 0
            if add == True:
                for i in range(len(adding)):
                    if adding[i].isdigit():
                        aux += int(adding[i])
                        if adding[i-1].isdigit():
                            bonus[j-1] *= 10
                            bonus[j-1] += aux
                        else:
                            bonus.append(aux)
                            j += 1
                        aux = 0
            szdice = int(szdice)
            ndice = int(ndice)
            for i in range(ndice):
                result.append(random.randrange(1, szdice+1, 1))

            total = 0
            for i in range(len(result)):
                total += result[i]

            for i in range(len(bonus)):
                total += bonus[i]

            crit = 0
            pifia = 0

            for i in range(ndice):
                if(result[i] == szdice):
                    crit += 1
                elif(result[i] == 1):
                    pifia += 1

            if crit == ndice:
                total_crit = True
                total_pifia = False
            elif pifia == ndice:
                total_crit = False
                total_pifia = True
            else:
                total_crit = False
                total_pifia = False

            to_send = 'El resultado es: **[{total}]** =>'.format(total=total)

            to_send += (' ([ *')
            for i in range(len(result)):
                if result[i] == szdice:
                    to_send += '**{result}**'.format(result=result[i])
                elif result[i] == 1:
                    to_send += '__{result}__'.format(result=result[i])
                else:
                    to_send += '{result}'.format(result=result[i])
                if i != len(result) - 1:
                    to_send += ' + '
            to_send += '* ] '

            for i in range(len(bonus)):
                to_send += ' + [{bonus}]'.format(bonus=bonus[i])

            to_send += ')'

            if total_crit:
                to_send += '\n +10 exp!'
            elif total_pifia:
                to_send += '\n F'

            return to_send

        else:
            return None
