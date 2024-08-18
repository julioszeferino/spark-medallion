from utils.bronze import cria_bronze
from utils.silver import cria_silver_fhvhv, cria_silver_corridas
from utils.gold import cria_gold
from utils.utils import consumer


def main():

    # Extract [E]
    cria_bronze()

    # Transform [T]
    cria_silver_fhvhv()
    cria_silver_corridas()

    # Load [L]
    cria_gold()

    # Consumer
    consumer()


if __name__ == '__main__':
    main()
