# adds higher directory to python modules path
import sys
sys.path.append("..")

# NOTE - run pytest with env var "SECRET_KEY="test" pytest" -v
from main import derive_page_nums, get_jwt, auth_redirect


class TestMain:
    def test_derive_page_nums(self):
        assert derive_page_nums(int_list=[i for i in range(100)], per_page=5) == [i for i in range(1,21)]
