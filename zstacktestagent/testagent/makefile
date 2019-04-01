ifndef GOROOT
    $(error GOROOT is not set)
endif

export GO=$(GOROOT)/bin/go
export GOPATH=$(shell pwd)

TARGET_DIR=target
PKG_TESTAGENT_DIR=$(TARGET_DIR)/pkg-testagent
PKG_TAR_DIR=$(TARGET_DIR)/pkg-tar

DEPS=github.com/Sirupsen/logrus github.com/pkg/errors github.com/fatih/structs golang.org/x/crypto/ssh github.com/tmc/scp

zvr:
	mkdir -p $(TARGET_DIR)
	$(GO) build -o $(TARGET_DIR)/testagent src/testagent/testagent.go

deps:
	$(GO) get $(DEPS)

clean:
	rm -rf target/

tar: zvr
	rm -rf $(PKG_TAR_DIR)
	mkdir -p $(PKG_TAR_DIR)
	cp -f $(TARGET_DIR)/testagent $(PKG_TAR_DIR)
	cp -f scripts/zstack-testagent $(PKG_TAR_DIR)
	tar czf $(TARGET_DIR)/testagent.tar.gz -C $(PKG_TAR_DIR) .

