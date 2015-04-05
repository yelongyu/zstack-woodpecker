class zstacktestagent_agent {
    $egg = "$zstackbase::params::basepath/zstacktestagent.egg"

    zstackbase::file_egg {"$egg":
        egg_source => "puppet:///modules/zstacktestagent/zstack-testagent.egg",
    }

    zstackbase::install_egg {"$egg":
        egg_subscribe => File["$egg"],
    }

    $service_file = "/etc/init.d/zstack-testagent"
    zstackbase::install_service_file {$service_file:
        file_source => "puppet:///modules/zstacktestagent/zstack-testagent",
    }

    zstackbase::agent_service {"zstack-testagent":
        service_subscribe => [Exec["install_$egg"], File[$service_file]],
    }
}

class zstacktestagent::entry {
    include zstackbase
    include zstacklib
    include zstacktestagent_agent

    Class['zstackbase'] -> Class['zstacklib'] -> Class['zstacktestagent_agent']
}
