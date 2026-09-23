package service

import (
    "fmt"
    corepkg "example.com/changeripple/sample/internal/core"
)

func Message() string { return fmt.Sprintf("%s", corepkg.Value()) }
