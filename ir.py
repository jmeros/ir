import argparse
import os
import sys

import pandas as pd

from src.calculo_ir import CalculoIr
from src.dropbox_files import upload_dropbox_file, OPERATIONS_FILEPATH
from src.envia_relatorio_por_email import envia_relatorio_html_por_email
from src.relatorio import relatorio_txt, relatorio_html, assunto
from src.stuff import get_operations, \
    merge_operacoes, \
    df_to_csv


def main(raw_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--do', required=False)
    parser.add_argument('--numero_de_meses', required=False, type=int, default=None)
    args = parser.parse_args(raw_args)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)

    if args.do == 'busca_trades_e_faz_merge_operacoes':
        do_busca_trades_e_faz_merge_operacoes()
        return

    if args.do == 'check_environment_variables':
        do_check_environment_variables()
        return

    if args.do == 'calculo_ir':
        do_calculo_ir(args.numero_de_meses)
        return

    do_busca_trades_e_faz_merge_operacoes()
    do_calculo_ir(args.numero_de_meses)


def do_busca_trades_e_faz_merge_operacoes():
    from src.crawler_cei import busca_trades
    df_cei = busca_trades(os.environ['CPF'], os.environ['SENHA_CEI'])

    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()

    df = get_operations()
    df = merge_operacoes(df, df_cei)
    df_to_csv(df, OPERATIONS_FILEPATH)

    upload_dropbox_file(OPERATIONS_FILEPATH, os.environ['DROPBOX_FILE_LOCATION'])


def do_check_environment_variables():
    from tests.test_environment_variables import TestEnvironmentVariables
    TestEnvironmentVariables().test_environment_variables()


def do_calculo_ir(numero_de_meses):
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()
    df = get_operations()

    from src.stuff import calcula_custodia

    calcula_custodia(df)
    calculo_ir = CalculoIr(df=df)
    calculo_ir.calcula()

    print(relatorio_txt(calculo_ir))

    envia_relatorio_html_por_email(assunto(calculo_ir),
                                   relatorio_html(calculo_ir, numero_de_meses))


if __name__ == "__main__":
    main(sys.argv[1:])