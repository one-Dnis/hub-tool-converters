import hashlib
from dataclasses import dataclass


@dataclass(kw_only=False, eq=False, order=False)
class AdditionalFields:
    dupe_key: str | None = None
    ruleId: str | None = None
    rule_description: str | None = None
    reason: str | None = None
    secret: str | None = None
    file_key: str | None = None

    def __parse_rule_id(self) -> None:

        if "Rule Id" in self.description:
            self.ruleId = self.description.split("**Rule Id:** ")[1].split("\n")[0]

        if self.vuln_id_from_tool:
            if not self.ruleId:
                self.ruleId = self.vuln_id_from_tool

    def __parse_reason(self) -> None:
        # Пример: "Hard coded {reason} found in {file_path}"
        #            0    1     !2!      3    4      5
        if self.title:
            self.reason = self.title.split()[2] if len(self.title.split()) > 2 else None

        if not self.reason and self.vuln_id_from_tool:
            self.reason = self.vuln_id_from_tool

    def __parse_secret(self) -> None:
        if "Secret:" in self.description:
            self.secret = self.description.split("**Secret:** ")[1].split("\n")[0]
        elif "Snippet:" in self.description:
            self.secret = self.description.split("**Snippet:**\n")[1]

    def __parse_file_key(self) -> None:
        if self.file_path is not None:
            self.file_key = hashlib.md5(
                self.file_path.encode('utf-8')
            ).hexdigest()

    def __parse_dupe_key(self) -> None:
        try:
            self.dupe_key = hashlib.md5(
                (self.title + self.secret + str(self.line) + self.file_path).encode("utf-8")
            ).hexdigest()
        except TypeError:
            self.dupe_key = hashlib.md5((self.title + self.file_path + str(self.line)).encode("utf-8")).hexdigest()

    def __parse_rule_description(self) -> None:
        self.rule_description = f'Hard coded {self.reason}'

    def parse_additional_fields(self) -> None:
        self.__parse_rule_id()
        self.__parse_reason()
        self.__parse_secret()
        self.__parse_file_key()
        self.__parse_dupe_key()
        self.__parse_rule_description()

    def check_additional_fields(self) -> None:
        if not self.ruleId:
            raise ValueError("ruleId not found")